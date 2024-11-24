from urllib.parse import quote
import httplib2, json
from uuid import uuid4
from google.cloud import bigquery, logging
from config import SERVICE_NAME, BASE_URL, SERVICE_ACCOUNT_EMAIL, SCOPES, MAX_TOKENS
from templates.inventory import QUERY as INVENTORY_QUERY_TEMPLATE
from templates.wiki import QUERY as WIKI_QUERY_TEMPLATE
import google.auth
from vertexai.generative_models import GenerationConfig
from flask import Flask
from flask_cors import CORS

def init_app(httplib2=httplib2):
    app = Flask(__name__)
    CORS(app)

    http = httplib2.Http()
    headers = {"Metadata-Flavor":"Google"}
    uri = 'http://metadata.google.internal/computeMetadata/v1/project/project-id'
    result = http.request(uri=uri, method='GET', headers=headers)
    project_id = result[1].decode()
    log_name = SERVICE_NAME
    
    creds, project = google.auth.default(scopes=SCOPES)
    return app, project_id, creds

def init_logger(project_id, log_name):
    res = logging.Resource(
        type="cloud_run_revision",
        labels={
            "project_id":project_id,
            "service_name":SERVICE_NAME
        }
    )
    log_client = logging.Client()
    logger_service = log_client.logger(log_name)
    logger_service.default_resource = res
    return logger_service



def task(uri, method='POST', params=None, base_url=BASE_URL, service_account_email=SERVICE_ACCOUNT_EMAIL):
    task = {
        "http_request": {
            "http_method":method,
            "url": base_url+uri+"?"+"&".join(["%s=%s"%(quote(str(key)), quote(str(value))) for key, value in params.items()]),
            "oidc_token":{
                "service_account_email":service_account_email,
                "audience": base_url
            }
        }
    }
    return task


def retrieve_session(session_id, s_bucket):
    if session_id is None:
        session_id = str(uuid4())
        session_logs = {
            'steps':[],
            'user_params':{
                'company':None,
                'position':None,
                'business_challenge':None
            },

        }
        p_dict_list = None
        g_dict_list = None
        topics_list = None
        scout_topics_list = None
        conversation_history = ''
        user_params = {}
    else:
        session_blob = s_bucket.get_blob(session_id)
        session_logs = json.loads(session_blob.download_as_string().decode())
        last_step = session_logs['steps'][-1]
        g_dict_list = json.loads(last_step.get('g_dict_list'))
        p_dict_list = json.loads(last_step.get('p_dict_list'))
        topics_list = json.loads(last_step.get('topics_list'))
        if topics_list is None and None not in  [g_dict_list, p_dict_list]:
            topics_list = g_dict_list + p_dict_list
        scout_topics_list = json.loads(last_step.get('scout_topics_list'))
        user_params = json.loads(last_step.get('user_params'))
        
        conversation_history = '\n'.join([f'user: {step["user_prompt"]}\nyou replied: {step["response"]}' for step in session_logs["steps"]])
    return session_id, conversation_history, topics_list, g_dict_list, p_dict_list, scout_topics_list, user_params, session_logs

def upload_session(session_id, s_bucket, session_logs, g_dict_list, p_dict_list, topics_list, scout_topics_list, user_params, user_prompt, response):
    session_blob = s_bucket.blob(session_id)
    current_step = {
        'g_dict_list':json.dumps(g_dict_list), 
        'p_dict_list': json.dumps(p_dict_list), 
        'topics_list': json.dumps(topics_list), 
        'scout_topics_list': json.dumps(scout_topics_list), 
        'user_params': json.dumps(user_params),
        'user_prompt': user_prompt,
        'response': response
    }
    session_logs['steps'].append(current_step)
    session_blob.upload_from_string(json.dumps(session_logs))
        




def get_llm_json(prompt, model, response_format, logger, max_tokens=MAX_TOKENS):
    generation_config = GenerationConfig(
            response_mime_type="application/json",
            response_schema=response_format,
            max_output_tokens=max_tokens,
            temperature=0.1,
            top_p=1,
        )
    response = model.generate_content(
          prompt,
          generation_config=generation_config,
      )
    # logger.log_text(response.text)
    return json.loads(response.text)

def get_artefacts(user_input, logger, session_id):
    query = INVENTORY_QUERY_TEMPLATE.format(
        input=user_input
    )
    logger.log_text(f'session {session_id}, query:\n{query}')
    bq_client = bigquery.Client()
    result = bq_client.query(query).result()
    result_rows = [dict(row) for row in result]
    
    
    return result_rows


def get_wiki(user_input, logger, session_id):
    query = WIKI_QUERY_TEMPLATE.format(
        input=user_input
    )
    logger.log_text(f'session {session_id}, query:\n{query}')
    bq_client = bigquery.Client()
    result = bq_client.query(query).result()
    result_rows = [dict(row) for row in result]
    
    
    return result_rows


