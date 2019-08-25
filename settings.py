import os

from dotenv import load_dotenv
load_dotenv()


SETTINGS = {
    'account_id': os.getenv('AWS_ACCOUNT_ID'),
    'region': os.getenv('AWS_REGION', 'us-east-1'),
    'ecr_name': os.getenv('AWS_ECR_NAME'),
    'state_file': {
        'bucket_name': os.getenv('AWS_STATE_FILE_BUCKET_NAME')
    }
}
