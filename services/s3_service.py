import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import List, Dict, Optional, Any


class S3Manager:
    def __init__(self):
        self.s3_client = None
        self.bucket_name = None

    def initialize_client(
        self, aws_access_key: str, aws_secret_key: str, region: str = "ap-south-1"
    ) -> bool:
        """Initialize S3 client with credentials"""
        try:
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=region,
            )
            # Test connection
            self.s3_client.list_buckets()
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to AWS: {str(e)}")

    def list_buckets(self) -> List[str]:
        """List all available S3 buckets"""
        try:
            response = self.s3_client.list_buckets()
            return [bucket["Name"] for bucket in response["Buckets"]]
        except Exception as e:
            raise Exception(f"Error listing buckets: {str(e)}")

    def list_objects(self, bucket_name: str, prefix: str = "") -> List[Dict]:
        """List objects in the specified bucket"""
        try:
            response = self.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)

            objects = []
            if "Contents" in response:
                for obj in response["Contents"]:
                    objects.append(
                        {
                            "Key": obj["Key"],
                            "Size": obj["Size"],
                            "LastModified": obj["LastModified"],
                            "StorageClass": obj.get("StorageClass", "STANDARD"),
                        }
                    )
            return objects
        except Exception as e:
            raise Exception(f"Error listing objects: {str(e)}")

    def upload_file(self, bucket_name: str, file_obj, object_name: str) -> bool:
        """Upload a file to S3 bucket"""
        try:
            self.s3_client.upload_fileobj(file_obj, bucket_name, object_name)
            return True
        except Exception as e:
            raise Exception(f"Error uploading file: {str(e)}")

    def download_file(self, bucket_name: str, object_name: str) -> Optional[bytes]:
        """Download a file from S3 bucket"""
        try:
            response = self.s3_client.get_object(Bucket=bucket_name, Key=object_name)
            return response["Body"].read()
        except Exception as e:
            raise Exception(f"Error downloading file: {str(e)}")

    def delete_file(self, bucket_name: str, object_name: str) -> bool:
        """Delete a file from S3 bucket"""
        try:
            self.s3_client.delete_object(Bucket=bucket_name, Key=object_name)
            return True
        except Exception as e:
            raise Exception(f"Error deleting file: {str(e)}")

    def get_file_info(self, bucket_name: str, object_name: str) -> Optional[Dict]:
        """Get detailed information about a file"""
        try:
            response = self.s3_client.head_object(Bucket=bucket_name, Key=object_name)
            return {
                "ContentLength": response["ContentLength"],
                "ContentType": response.get("ContentType", "Unknown"),
                "LastModified": response["LastModified"],
                "ETag": response["ETag"].strip('"'),
                "StorageClass": response.get("StorageClass", "STANDARD"),
            }
        except Exception as e:
            raise Exception(f"Error getting file info: {str(e)}")
