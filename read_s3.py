import boto3

bucket_name = "waterdip-data-lake"
file_name = "hello.txt"

s3 = boto3.client("s3")

response = s3.get_object(
    Bucket=bucket_name,
    Key=file_name
)

content = response["Body"].read().decode("utf-8")

print(content)