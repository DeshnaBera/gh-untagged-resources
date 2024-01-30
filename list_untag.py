import boto3
import botocore
import csv
 
def get_resources_without_tags(service, mandatory_tags):
    client = boto3.client(service)
    resources = []
    if service == 's3':
        response = client.list_buckets()
        for bucket in response['Buckets']:
            try:
                bucket_tagging = client.get_bucket_tagging(Bucket=bucket['Name'])
                bucket_tags = set(tag['Key'] for tag in bucket_tagging['TagSet'])
                if not set(mandatory_tags).issubset(bucket_tags):
                    resources.append(bucket['Name'])
            except botocore.exceptions.ClientError as e:
                # if e.response['Error']['Code'] == 'NoSuchTagSet':
                resources.append(bucket['Name'])
                # else:
                #     raise
    elif service == 'lambda':
        response = client.list_functions()
        for function in response['Functions']:
            function_tags = client.list_tags(Resource=function['FunctionArn'])
            if not set(mandatory_tags).issubset(function_tags['Tags']):
                resources.append(function['FunctionName'])
    # elif service == 'dynamodb':
    #     response = client.list_tables()
    #     for table in response['TableNames']:
    #         table_tags = client.list_tags_of_resource(ResourceArn=table)
    #         if not set(mandatory_tags).issubset(table_tags['Tags']):
    #             resources.append(table)
    return resources
 
def generate_report(service, resources):
    with open(f'{service}_report.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Resource Name"])
        for resource in resources:
            writer.writerow([resource])
 
def main():
    services = ['s3', 'lambda', 'dynamodb']
    mandatory_tags = ['Name']
    for service in services:
        resources = get_resources_without_tags(service, mandatory_tags)
        generate_report(service, resources)
        print(f'For {service}, {len(resources)} resources do not have the mandatory tags')
 
if __name__ == "__main__":
    main()