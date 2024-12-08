


QUERY = """with query_embedding as (
SELECT * FROM
  ML.GENERATE_EMBEDDING(
    MODEL `wiki.wiki-embedding`,
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
    TABLE `wiki.wiki_vdb`,
    'ml_generate_embedding_result',
    TABLE query_embedding,
    top_k => 50,
    distance_type => 'EUCLIDEAN',
    -- distance_type => 'COSINE',
    options => '{{"use_brute_force":true}}'
  ))

select distinct * except(id), from candidate_ids join `wiki.wiki` wiki
on candidate_ids.id = concat(wiki.page_name, '|', wiki.section)
where distance < .8 order by distance limit 5
"""



PROMPT = """you are Anne, the descendant of engineer, scientist, entrepreneur and philantropist Marc Seguin. 
You are helping users discover the rich history of Marc Seguin's life, and you already had the following conversation:
{conversation_history}

Use the only following elements to write a response to the user's last question. Do not extrapolate from your general knowledge.
{wiki_string}
    """


FORMAT = {
    'type': 'ARRAY',
    'items': {
        'type': 'OBJECT',
        'properties': {
            'response': {'type': 'STRING'}
        },
  'required': [
      'response'
      ]
  }
}


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
