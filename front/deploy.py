import os
from config import SERVICE_NAME, REGION, IMAGE_NAME

#stream = os.popen(f'gcloud config set builds/use_kaniko True')
#stream = os.popen(f'gcloud builds submit --tag {IMAGE_NAME} .')
#stream = os.popen(f'gcloud run deploy {SERVICE_NAME} --image {IMAGE_NAME} --region {REGION}')

# os.system(f'gcloud config set builds/use_kaniko True')
# os.system(f'gcloud builds submit --tag {IMAGE_NAME} .')
# os.system(f'gcloud run deploy {SERVICE_NAME} --image {IMAGE_NAME} --region {REGION}')

print(f'gcloud config set builds/use_kaniko True')
# print(f'gcloud builds submit --tag {IMAGE_NAME} .')
# print(f'gcloud run deploy {SERVICE_NAME} --image {IMAGE_NAME} --region {REGION}')


os.system(f'gcloud run deploy {SERVICE_NAME} --source . --region {REGION}')
