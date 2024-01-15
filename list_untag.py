import boto3

def list_untagged_lambda_functions():
    lambda_client = boto3.client('lambda')
    response = lambda_client.list_functions()
    untagged_functions = []
    for function in response['Functions']:
        tags = lambda_client.list_tags(Resource=function['FunctionArn'])
        if 'Tags' not in tags:
            untagged_functions.append(function['FunctionName'])
    return untagged_functions
