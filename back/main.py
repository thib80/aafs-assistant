import os, re, json, time
from flask import Flask
import flask
from datetime import datetime
from google.cloud import storage, bigquery #, tasks_v2
from utils import init_app, init_logger, get_llm_json, get_artefacts, retrieve_session, upload_session, get_wiki
from config import SERVICE_NAME, REGION, SESSION_BUCKET_NAME, COMPLEX_MODEL_NAME , MAX_TOKENS, RESPONSE_HTML
from templates.inventory import FORMAT as INVENTORY_FORMAT, HTML as INVENTORY_HTML_TEMPLATE
from templates.wiki import PROMPT as WIKI_PROMPT, FORMAT as WIKI_FORMAT
from google.api_core.exceptions import InvalidArgument
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import vertexai.preview.generative_models as generative_models

app, project_id, creds = init_app()
logger = init_logger(project_id, SERVICE_NAME)
def log(log_text):
    logger.log_text(log_text, severity='INFO')

gs_client = storage.Client()
s_bucket = gs_client.get_bucket(SESSION_BUCKET_NAME)
vertexai.init(project=project_id, location=REGION)
complex_model = GenerativeModel(COMPLEX_MODEL_NAME)


@app.route("/process", methods=['GET', 'POST'])
def process():
    start_ts = datetime.now()
    logger.log_text(flask.request.data.decode())
    params = json.loads(flask.request.data.decode())
    logger.log_struct(params)

    user_prompt = params['message']
    session_id = params.get('sessionId')
    logger.log_text(f'user input: {user_prompt}, session id: {session_id}')
    
    

    session_id, conversation_history, topics_list, g_dict_list, p_dict_list, scout_topics_list, user_params, session_logs = retrieve_session(session_id, s_bucket)
    conversation_history += f'\nuser: {user_prompt}'
   
    prompt = f"""you are Anne, the descendant of engineer, scientist, entrepreneur and philantropist Marc Seguin. 
    You have access to a database that contains the inventory of Varagnes, Marc Seguin's house.
    You also have access to Marc Seguin's detail biography.
    The collection holds various artefacts, ranging from science instruments to books and letters.
    From the conversation history below, assess whether the user is interested in 
    - certain pieces of the inventory, in which case reply with intent "inventory"
    - is curious about the life of Marc Seguin, in which case reply with intent "marc"
    For all these intents, store in 'response' the query that could be used to retrieve relevant artefacts from their descriptions embeddings. Make sure that you only retain meaningful keywords and remove generic ones.
    Otherwise just reply with intent "generic" and respond with the appropriate response (in french) so that the user understands what you can do for him.
    Here is the conversation history:
    {conversation_history}
    """
    logger.log_text(f'session {session_id}, prompt\n{prompt}')
    json_response = get_llm_json(prompt, complex_model, INVENTORY_FORMAT, logger)[0]
    logger.log_text(f'session {session_id}, intent response\n{json.dumps(json_response)}')

    intent = json_response['intent']    
    if intent == 'generic':
        response = json_response['response']
        log_response = response
    elif intent == 'inventory':
        user_input = json_response['response']
        artefacts = get_artefacts(user_input.lower().replace('seguin', ''), logger, session_id)
        
        if len(artefacts) > 0:
            html_lines = []
            for artefact_dict in artefacts:
                title = f"{artefact_dict['title']} (source:{artefact_dict['source']})"
                url = None
                if artefact_dict['url_large'] == 'None':
                    if artefact_dict['url_medium'] == 'None':
                        url = artefact_dict['url_small']
                    else:
                        url = artefact_dict['url_medium']
                else:
                    url = artefact_dict['url_large']
                img_html = f'<a href="{url}" target="_blank"><img src="{url}" alt="{title}"/></a>' if url != 'None' else ''
        
        if len(artefacts) > 0:
            html_lines = []
            for artefact_dict in artefacts:
                title = f"{artefact_dict['title']} (source:{artefact_dict['source']})"
                url = None
                if artefact_dict['url_large'] == 'None':
                    if artefact_dict['url_medium'] == 'None':
                        url = artefact_dict['url_small']
                    else:
                        url = artefact_dict['url_medium']
                else:
                    url = artefact_dict['url_large']
                img_html = f'<a href="{url}" target="_blank"><img src="{url}" alt="{title}"/></a>' if url != 'None' else ''

                description = artefact_dict['description']
                html_lines.append(INVENTORY_HTML_TEMPLATE.format(title=title, img_html=img_html, description=description))
            
            logger.log_text(f'session {session_id}, retrieved artefacts\n{json.dumps(artefacts)}')
            logger.log_text(f'session id: {session_id}, elapsed {(datetime.now() - start_ts).total_seconds()}')
            response = """J'ai trouvé ces résultats qui pourraient vous intéresser.<br><br>"""
            response += '<br><br>'.join(html_lines)
            log_response = 'voici des résultats qui peuvent vous intéresser'
        else:
            response = "Je suis désolée mais je n'ai rien trouvé dans l'inventaire à ce sujet"
            log_response = response
    elif intent == 'marc':
        user_input = json_response['response']
        sections = get_wiki(user_input, logger, session_id)
        if len(sections) != 0:
            wiki_string = '\n\n'.join([f"{row_dict['section']}:\n{row_dict['text']}" for row_dict in sections])
            wiki_prefix = 'https://fr.wikipedia.org/wiki/' 
            sources_urls = [f"{wiki_prefix}{row_dict['page_name']}#{row_dict['section'].split('^')[-1].replace(' ', '_')}" for row_dict in sections]
            sources = '<br>'.join([f'<a href="{url}" target="_blank">{url}</a>' for url in sources_urls])
            
            prompt = WIKI_PROMPT.format(conversation_history=conversation_history, wiki_string=wiki_string)
            wiki_response = get_llm_json(prompt, complex_model, WIKI_FORMAT, logger)[0]['response'].replace('\n', '<br>')
            logger.log_text(f'session {session_id}, llm response\n{wiki_response}')
            
            logger.log_text(f'session {session_id}, retrieved sections\n{json.dumps(sections)}')
            logger.log_text(f'session id: {session_id}, elapsed {(datetime.now() - start_ts).total_seconds()}')
            response = f"{wiki_response}<br><p><small>source(s):<br>{sources}</small></p>"
            log_response = wiki_response
        else:
            response = f"Désolée, je n'ai rien trouvé dans mes archives"
            log_response = response

        
    upload_session(session_id, s_bucket, session_logs, g_dict_list, p_dict_list, topics_list, scout_topics_list, user_params, user_prompt, log_response)
    logger.log_text(f'session {session_id}: response\n{response}')
    logger.log_text(f'session id: {session_id}, elapsed {(datetime.now() - start_ts).total_seconds()}')
    return {'html':RESPONSE_HTML.format(response=response) , 'sessionId':session_id}    
    
    


    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))