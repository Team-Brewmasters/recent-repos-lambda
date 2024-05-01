import json

import boto3


def lambda_handler(event, context):
    try:



        # Get the search query from the event
        recent_searches = get_recent_searches()

        # Clean up old searches
        clean_up_old_searches()

        
        return {
            'statusCode': 200,
            'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
                },
            'body': json.dumps({
                'recentSearches': recent_searches
            })
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
    

def get_recent_searches():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('recent_repos')
    
    response = table.scan(Limit=1000)  # Consider using a more efficient query method in the future
    items = response['Items']
    # Sort by timestamp in descending order and pick the top 3, then extract only the URLs
    recent_urls = [item['repositoryURL'] for item in sorted(items, key=lambda x: int(x['searchTimestamp']), reverse=True)[:3]]
    return recent_urls

    
def clean_up_old_searches():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('recent_repos')
    
    # Scan to get all items
    response = table.scan()
    items = response['Items']
    
    # If there are more than 3 items, delete the oldest
    if len(items) > 3:
        # Sort items by timestamp
        sorted_items = sorted(items, key=lambda x: x['searchTimestamp'])
        # Delete all but the last three items
        for item in sorted_items[:-3]:
            table.delete_item(
                Key={
                    'searchTimestamp': item['searchTimestamp']
                }
            )
