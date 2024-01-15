import boto3

def list_untagged_s3_buckets():
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    untagged_buckets = []
    for bucket in response['Buckets']:
        tags = s3.get_bucket_tagging(Bucket=bucket['Name'])
        if 'TagSet' not in tags:
            untagged_buckets.append(bucket['Name'])
    return untagged_buckets
