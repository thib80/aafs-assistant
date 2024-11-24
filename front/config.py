SERVICE_NAME = 'anne'
REGION = 'europe-west6'
PROJECT = 'amis-fondation-seguin'
PROJECT_NUMBER = '303057230676'

IMAGE_NAME = f'{REGION}-docker.pkg.dev/{PROJECT}/cloud-run-source-deploy/{SERVICE_NAME}:latest'
SERVICE_ACCOUNT_EMAIL = f'{PROJECT_NUMBER}-compute@developer.gserviceaccount.com'
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/bigquery',
    'https://www.googleapis.com/auth/cloud-vision'
]

TAXONOMY_BUCKET_NAME = 'ip-knowledge-base-sb'
TAXONOMY_BLOB_NAME = 'taxonomy/taxonomy_dict'
VISION_OCR_MAX_PAGES = 5

HELLO_WORLD_HTML = """<!DOCTYPE html>
<html>
<head>
  <title>Hello World</title>
</head>
<body>
  <h4>Hello, world!</h4>
</body>
</html>"""