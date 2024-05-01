import boto3

class DynamoCacheService:
    def __init__(self, table_name):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)

    def put_question(self, question, repo, answer):
        try: 
            self.table.put_item(
                Item={
                    'question': question,
                    'repo': repo,
                    'answer': answer
                }
            )
        except Exception as e:
            print(f"Error: {e}")

    def get_question(self, question, repo):
        response = self.table.get_item(
            Key={
                'question': question,
                'repo': repo
            }
        )
        item = response.get('Item')
        return item if item else None