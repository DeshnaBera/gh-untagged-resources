import boto3

def list_untagged_s3_buckets():
    session = boto3.Session(
        aws_access_key_id='AKIAXCMHLBE24P6BZKOI',
        aws_secret_access_key='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'
    )
    s3 = session.client('s3')
    response = s3.list_buckets()
    untagged_buckets = []
    for bucket in response['Buckets']:
        tags = s3.get_bucket_tagging(Bucket=bucket['Name'])
        if 'TagSet' not in tags:
            untagged_buckets.append(bucket['Name'])
    return untagged_buckets
