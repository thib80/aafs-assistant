PROMPT = """
You are the helpful assistant of users who ultimately aim at identifying startups that could help them adress business challenges via open innovation.
Today the user works as {position} at {company} and is interested in {business_challenge}
The following topics and associated characteristics have already been identified:
{p_topics_string}
Using your general knowledge, and only if you believe you can find something relevant, identify some additional topics using the same format
keep in mind that your response is limited to {max_tokens} tokens """

UPDATE_PROMPT = """
You are the helpful assistant of users who ultimately aim at identifying startups that could help them adress business challenges via open innovation.
Below is a history of your conversation so far:
{conversation_history}
The following topics and associated characteristics have already been identified:
{topics_string}

Considering the user's last input, and using your general knowledge, make the appropriate changes to the topics list, updating, adding or removing them as you see fit.
keep in mind that your response is limited to {max_tokens} tokens"""

FORMAT = {
    'type': 'ARRAY',
    'items': {
        'type': 'OBJECT',
        'properties': {
            'intent': {'type': 'STRING'},
            'response': {'type': 'STRING'}
        },
  'required': ['intent',
            'response'
          ]
  }
}


QUERY = """with query_embedding as (
SELECT * FROM
  ML.GENERATE_EMBEDDING(
    MODEL `u_nantes.embedding-gecko`,
    (SELECT '{input}' as title, '{input}' as content),
    STRUCT(TRUE AS flatten_json_output, 'SEMANTIC_SIMILARITY' as task_type)
  )
)
,candidate_ids as (

  SELECT
  query.title as query_title,
  base.title as id,
  distance as distance
FROM
  VECTOR_SEARCH(
    TABLE `u_nantes.vector_db_safe`,
    'ml_generate_embedding_result',
    TABLE query_embedding,
    top_k => 50,
    distance_type => 'EUCLIDEAN',
    -- distance_type => 'COSINE',
    options => '{{"use_brute_force":true}}'
  ))

select distinct * except(id), 'https://epotec.univ-nantes.fr' as source from candidate_ids join `u_nantes.inventaires` using (id)
where distance < 0.8 order by distance limit 5
"""


HTML = """
<div class="section">
  <div class="problem">
    <p>{title}</p>
    {img_html}
    <ul>
      <li>{description}.</li>
    </ul>
    </div>
</div>"""
