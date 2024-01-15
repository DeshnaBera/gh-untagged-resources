# Import boto3 library
import boto3

# Define the mandatory tags for Terraform resources
mandatory_tags = ["Name", "Environment", "Owner"]

# Define the resource types to check
resource_types = ["s3", "lambda", "dynamodb"]

# Create a dictionary to store the results
results = {}

# Loop through each resource type
for resource_type in resource_types:
    # Create a boto3 client for the resource type
    client = boto3.client(resource_type)
    
    # Get the list of resources for the resource type
    if resource_type == "s3":
        # For s3, use list_buckets method
        resources = client.list_buckets()["Buckets"]
    elif resource_type == "lambda":
        # For lambda, use list_functions method
        resources = client.list_functions()["Functions"]
    elif resource_type == "dynamodb":
        # For dynamodb, use list_tables method
        resources = client.list_tables()["TableNames"]
    
    # Loop through each resource
    for resource in resources:
        # Get the resource name or id
        if resource_type == "s3":
            # For s3, use the bucket name
            resource_name = resource["Name"]
        elif resource_type == "lambda":
            # For lambda, use the function name
            resource_name = resource["FunctionName"]
        elif resource_type == "dynamodb":
            # For dynamodb, use the table name
            resource_name = resource
        
        # Get the resource tags
        if resource_type == "s3":
            # For s3, use get_bucket_tagging method
            try:
                resource_tags = client.get_bucket_tagging(Bucket=resource_name)["TagSet"]
            except:
                # If the bucket has no tags, set an empty list
                resource_tags = []
        elif resource_type == "lambda":
            # For lambda, use list_tags method
            resource_tags = client.list_tags(Resource=resource["FunctionArn"])["Tags"]
        elif resource_type == "dynamodb":
            # For dynamodb, use list_tags_of_resource method
            resource_tags = client.list_tags_of_resource(ResourceArn=resource["TableArn"])["Tags"]
        
        # Convert the resource tags to a dictionary
        resource_tags_dict = {tag["Key"]: tag["Value"] for tag in resource_tags}
        
        # Check if the resource has all the mandatory tags
        has_mandatory_tags = True
        for tag in mandatory_tags:
            if tag not in resource_tags_dict:
                # If any mandatory tag is missing, set the flag to False
                has_mandatory_tags = False
                break
        
        # If the resource does not have all the mandatory tags, add it to the results
        if not has_mandatory_tags:
            # If the resource type is not in the results, create a new list
            if resource_type not in results:
                results[resource_type] = []
            # Append the resource name and tags to the results
            results[resource_type].append((resource_name, resource_tags_dict))

# Print the results
print("The following resources are not managed by Terraform:")
for resource_type, resource_list in results.items():
    print(f"- {resource_type}:")
    for resource_name, resource_tags in resource_list:
        print(f"  - {resource_name}: {resource_tags}")
