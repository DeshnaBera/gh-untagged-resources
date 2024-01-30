import boto3
import botocore
import csv

def get_resources_without_tags(service, mandatory_tags, region_name=None):
    if region_name:
        client = boto3.client(service, region_name=region_name)
    else:
        client = boto3.client(service)
    resources = []
    if service == 's3':
        response = client.list_buckets()
        for bucket in response['Buckets']:
            try:
                bucket_tagging = client.get_bucket_tagging(Bucket=bucket['Name'])
                bucket_tags = set(tag['Key'] for tag in bucket_tagging['TagSet'])
                if not set(mandatory_tags).issubset(bucket_tags):
                    resources.append((bucket['Name'], client.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint']))
            except botocore.exceptions.ClientError as e:
                resources.append((bucket['Name'], client.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint']))
    elif service == 'lambda':
        response = client.list_functions()
        for function in response['Functions']:
            function_tags = client.list_tags(Resource=function['FunctionArn'])
            if not set(mandatory_tags).issubset(function_tags['Tags']):
                resources.append((function['FunctionName'], region_name))
    elif service == 'dynamodb':
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
    with open(f'{service}_report.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Resource Name", "Region"])
        for resource in resources:
            writer.writerow(resource)

def main():
    services = ['s3', 'lambda', 'dynamodb']
    mandatory_tags = ['Name']
    ec2 = boto3.client('ec2')
    regions = [region['RegionName'] for region in ec2.describe_regions()['Regions']]
    for service in services:
        if service == 's3':
            resources = get_resources_without_tags(service, mandatory_tags)
            generate_report(service, resources)
            print(f'For {service}, {len(resources)} resources do not have the mandatory tags')
        else:
            for region_name in regions:
                resources = get_resources_without_tags(service, mandatory_tags, region_name)
                generate_report(service, resources)
                print(f'For {service} in {region_name}, {len(resources)} resources do not have the mandatory tags')

if __name__ == "__main__":
    main()
