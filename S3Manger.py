import os
import boto3


class S3Manager:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv(
                'AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('REGION')
        )

    def upload_fileobj(self, data, bucket_name, key):
        self.s3.upload_fileobj(data, bucket_name, key)

    def upload_file(self, path, bucket_name, key):
        self.s3.upload_file(path, bucket_name, key)

    def download_file(self, key, bucket_name):
        local_file_path = os.path.join(
            os.path.expanduser('~'), 'Downloads', key)
        self.s3.download_file(bucket_name, key, local_file_path)

    def list_files(self, bucket_name):
        response = self.s3.list_objects(Bucket=bucket_name)
        return [item["Key"] for item in response["Contents"]]

    def get_url(self, bucket_name, key):
        return self.s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": key},
            ExpiresIn=3600
        )
