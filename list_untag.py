import boto3
def list_untagged_resources(resource_type, aws_access_key_id, aws_secret_access_key, region):
   client = boto3.client(
       resource_type,
       aws_access_key_id=aws_access_key_id,
       aws_secret_access_key=aws_secret_access_key,
       region_name=region
   )
   untagged_resources = []
   # Add logic to fetch resources without tags for each resource type
   if resource_type == 's3':
       # Sample logic for S3
       buckets = client.list_buckets()['Buckets']
       for bucket in buckets:
           tags = client.get_bucket_tagging(Bucket=bucket['Name']).get('TagSet', [])
           if not tags:
               untagged_resources.append({'Type': 'S3 Bucket', 'Name': bucket['Name']})
   elif resource_type == 'lambda':
       # Sample logic for Lambda
       functions = client.list_functions()['Functions']
       for function in functions:
           tags = client.list_tags(Resource=function['FunctionArn']).get('Tags', {})
           if not tags:
               untagged_resources.append({'Type': 'Lambda Function', 'Name': function['FunctionName']})
   elif resource_type == 'dynamodb':
       # Sample logic for DynamoDB
       tables = client.list_tables()['TableNames']
       for table in tables:
           tags = client.list_tags_of_resource(ResourceArn=f'arn:aws:dynamodb:{region}:{aws_access_key_id}:table/{table}').get('Tags', {})
           if not tags:
               untagged_resources.append({'Type': 'DynamoDB Table', 'Name': table})
   return untagged_resources
# Example usage
aws_access_key_id = 'AKIAXCMHLBE24P6BZKOI'
aws_secret_access_key = 'qfmMlzvBMRRz0aM0buQ2cEICl2PMur80d8Q2LYZc'
region = 'us-east-1'
untagged_s3 = list_untagged_resources('s3', aws_access_key_id, aws_secret_access_key, region)
untagged_lambda = list_untagged_resources('lambda', aws_access_key_id, aws_secret_access_key, region)
untagged_dynamodb = list_untagged_resources('dynamodb', aws_access_key_id, aws_secret_access_key, region)
print("Untagged S3 Buckets:", untagged_s3)
print("Untagged Lambdas:", untagged_lambda)
print("Untagged DynamoDB Tables:", untagged_dynamodb)