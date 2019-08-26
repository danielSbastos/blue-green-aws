import os

from dotenv import load_dotenv
load_dotenv()


SETTINGS = {
    'account_id': os.getenv('AWS_ACCOUNT_ID'),
    'region': os.getenv('AWS_REGION', 'us-east-1'),
    'ecr': {
        'repo_name': os.getenv('AWS_ECR_NAME'),
        'image_name': os.getenv('AWS_ECR_IMAGE_NAME')
    },
    'state_file': {
        'bucket_name': os.getenv('AWS_STATE_FILE_BUCKET_NAME')
    }
}
