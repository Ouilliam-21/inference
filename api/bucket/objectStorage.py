import boto3
import os
from botocore.client import Config


class ObjectStorage:
    def __init__(self):
        print("🫎 Initializing ObjectStorage")
        self.session = boto3.session.Session()
        self.bucket, self.region, self.access_key, self.secret_key = self._load_env()
        self.client = self.session.client(
            's3',
            region_name=self.region,
            endpoint_url=f'https://{self.region}.digitaloceanspaces.com',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(s3={'addressing_style': 'virtual'})

        )
        print(f"🫎 ObjectStorage initialized with bucket: {self.bucket} and region: {self.region}")

    def _load_env(self):
        bucket = os.getenv("DIGITAL_OCEAN_SPACE_NAME")
        region = os.getenv("DIGITAL_OCEAN_SPACE_REGION")
        access_key = os.getenv("DIGITAL_OCEAN_SPACE_ACCESS_KEY")
        secret_key = os.getenv("DIGITAL_OCEAN_SPACE_SECRET_KEY")

        if not bucket:
            raise ValueError("required env DIGITAL_OCEAN_SPACE_NAME")

        if not region:
            raise ValueError("required env DIGITAL_OCEAN_SPACE_REGION")

        if not access_key:
            raise ValueError("required env DIGITAL_OCEAN_SPACE_ACCESS_KEY")

        if not secret_key:
            raise ValueError("required env DIGITAL_OCEAN_SPACE_SECRET_KEY")

        return bucket, region, access_key, secret_key

    def upload(self, filename: str):
        self.client.upload_file(filename, self.bucket, filename,            ExtraArgs={'ACL': 'public-read'})
        file_url = f"https://{self.bucket}.{self.region}.digitaloceanspaces.com/{filename}"
        return file_url


