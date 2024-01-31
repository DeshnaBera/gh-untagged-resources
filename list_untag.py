import os
import boto3
import botocore
import csv
 
def get_s3_resources_without_tags(mandatory_tags):
    client = boto3.client('s3')
    resources = []
    response = client.list_buckets()
    for bucket in response['Buckets']:
        try:
            bucket_tagging = client.get_bucket_tagging(Bucket=bucket['Name'])
            bucket_tags = set(tag['Key'] for tag in bucket_tagging['TagSet'])
            if not set(mandatory_tags).issubset(bucket_tags):
                resources.append((bucket['Name'], client.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint']))
        except botocore.exceptions.ClientError as e:
            resources.append((bucket['Name'], client.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint']))
    return resources
 
def get_lambda_resources_without_tags(mandatory_tags, region_name):
    client = boto3.client('lambda', region_name=region_name)
    resources = []
    response = client.list_functions()
    for function in response['Functions']:
        function_tags = client.list_tags(Resource=function['FunctionArn'])
        if not set(mandatory_tags).issubset(function_tags['Tags']):
            resources.append((function['FunctionName'], region_name))
    return resources
 
def get_dynamodb_resources_without_tags(mandatory_tags, region_name):
    client = boto3.client('dynamodb', region_name=region_name)
    resources = []
    paginator = client.get_paginator('list_tables')
    for page in paginator.paginate():
        for table_name in page['TableNames']:
            try:
                response = client.list_tags_of_resource(ResourceArn=f'arn:aws:dynamodb:{region_name}:table/{table_name}')
                table_tags = {tag['Key']: tag['Value'] for tag in response['Tags']}
                if not set(mandatory_tags).issubset(table_tags):
                    resources.append((table_name, region_name))
            except botocore.exceptions.ClientError as e:
                resources.append((table_name, region_name))
    return resources
 
def generate_report(service, resources):
    file_exists = os.path.isfile(f'{service}_report.csv')
    with open(f'{service}_report.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Resource Name", "Region"])
        for resource in resources:
            writer.writerow(resource)
 
def main():
    mandatory_tags = ['Name']
    ec2 = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]
 
    s3_resources = get_s3_resources_without_tags(mandatory_tags)
    generate_report('s3', s3_resources)
    print(f'For s3, {len(s3_resources)} resources do not have the mandatory tags')
 
    for region_name in regions:
        lambda_resources = get_lambda_resources_without_tags(mandatory_tags, region_name)
        generate_report('lambda', lambda_resources)
        print(f'For lambda in {region_name}, {len(lambda_resources)} resources do not have the mandatory tags')
    for region_name in regions:
        dynamodb_resources = get_dynamodb_resources_without_tags(mandatory_tags, region_name)
        generate_report('dynamodb', dynamodb_resources)
        print(f'For dynamodb in {region_name}, {len(dynamodb_resources)} resources do not have the mandatory tags')
 
if __name__ == "__main__":
    main()