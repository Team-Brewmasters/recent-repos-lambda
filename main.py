import json

from github_api_service import get_repo_file_contents
from open_ai_service import call_chatgpt
from dynamo_cache_service import DynamoCacheService


def lambda_handler(event, context):
    try:



        github_url = event['queryStringParameters']['githubURL']
        question = event['queryStringParameters']['question']
        _, _, username, repo_name = github_url.rstrip('/').split('/')[-4:]

        dynamo_rk = f"{username}{repo_name}"

        dynamo_cache_service = DynamoCacheService('questions')

        cache_data = dynamo_cache_service.get_question(question, dynamo_rk)

        if cache_data is not None:
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
                },
                'body': json.dumps(cache_data['answer'])
            }

        file_content = get_repo_file_contents(github_url)

        open_ai_response = call_chatgpt(question, file_content)

        dynamo_cache_service.put_question(question, dynamo_rk, open_ai_response)
        
        return {
            'statusCode': 200,
            'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
                },
            'body': json.dumps(open_ai_response)
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': str(e),
            'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET,OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
                },
        }
    
