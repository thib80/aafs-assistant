

SERVICE_NAME = 'anne-backend'
REGION = 'europe-west6'
PROJECT = 't-innopearl-sandbox'
PROJECT_NUMBER = '303057230676'
BASE_URL = 'https://process-corpus-32scxi5uja-oa.a.run.app'
IMAGE_NAME = f'{REGION}-docker.pkg.dev/{PROJECT}/cloud-run-source-deploy/{SERVICE_NAME}:latest'
SERVICE_ACCOUNT_EMAIL = f'{PROJECT_NUMBER}-compute@developer.gserviceaccount.com'
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/bigquery',
    'https://www.googleapis.com/auth/cloud-vision'
]
SESSION_BUCKET_NAME = 'aafs-chatbot-sessions'

COMPLEX_MODEL_NAME = "gemini-1.5-pro"
FAST_MODEL_NAME = "gemini-1.5-flash"

MAX_TOKENS = 8092

# RESPONSE_HTML = """<!DOCTYPE html>
# <html>
# <head>
#   <title>Hello World</title>
# </head>
# <body>
#   <p>{response}</p>
# </body>
# </html>"""


RESPONSE_HTML = """<!DOCTYPE html>
<html>
<body>
  <p>{response}</p>
</body>
</html>"""