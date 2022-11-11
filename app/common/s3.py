import logging
import boto3
from botocore.exceptions import ClientError

from ..config import settings

s3_client = boto3.client('s3', 
    region_name=settings.region,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key
)

# Print out bucket names
# response = s3_client.list_buckets()
# print(response["Buckets"])

def create_presigned_url(object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """
    bucket_name = settings.bucket_name

    # Generate a presigned URL for the S3 object
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        print(e)
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response

# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.upload_file
async def upload_file_in_s3(key, fileobj):
    bucket_name = settings.bucket_name
    return s3_client.upload_fileobj(fileobj.file, bucket_name, key)

# Upload a new file
# with open('/home/bijayincanada/Downloads/bbdn.jpg', 'rb') as data:
#     s3_client.upload_fileobj(data, "bucket_name", 'key')