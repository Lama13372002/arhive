"""S3-compatible storage client."""

import boto3
from botocore.exceptions import ClientError
from typing import Optional, Dict, Any
import structlog

from core.config import settings

logger = structlog.get_logger()


class S3Client:
    """S3-compatible storage client."""
    
    def __init__(self):
        self.endpoint_url = settings.s3_endpoint_url
        self.access_key_id = settings.s3_access_key_id
        self.secret_access_key = settings.s3_secret_access_key
        self.bucket_name = settings.s3_bucket_name
        self.region = settings.s3_region
        
        # Initialize S3 client
        self.client = boto3.client(
            's3',
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name=self.region
        )
    
    async def upload_file(self, file_path: str, key: str, metadata: Optional[Dict[str, str]] = None) -> str:
        """Upload file to S3."""
        try:
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.client.upload_file(
                file_path,
                self.bucket_name,
                key,
                ExtraArgs=extra_args
            )
            
            url = f"{self.endpoint_url}/{self.bucket_name}/{key}"
            logger.info("File uploaded successfully", key=key, url=url)
            
            return url
            
        except ClientError as e:
            logger.error("S3 upload error", error=str(e), key=key)
            raise Exception(f"S3 upload error: {str(e)}")
    
    async def upload_fileobj(self, file_obj, key: str, metadata: Optional[Dict[str, str]] = None) -> str:
        """Upload file object to S3."""
        try:
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.client.upload_fileobj(
                file_obj,
                self.bucket_name,
                key,
                ExtraArgs=extra_args
            )
            
            url = f"{self.endpoint_url}/{self.bucket_name}/{key}"
            logger.info("File object uploaded successfully", key=key, url=url)
            
            return url
            
        except ClientError as e:
            logger.error("S3 upload error", error=str(e), key=key)
            raise Exception(f"S3 upload error: {str(e)}")
    
    def generate_presigned_url(self, key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for file access."""
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
            
            logger.info("Presigned URL generated", key=key, expiration=expiration)
            return url
            
        except ClientError as e:
            logger.error("S3 presigned URL error", error=str(e), key=key)
            raise Exception(f"S3 presigned URL error: {str(e)}")
    
    def generate_presigned_upload_url(self, key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for file upload."""
        try:
            url = self.client.generate_presigned_url(
                'put_object',
                Params={'Bucket': self.bucket_name, 'Key': key},
                ExpiresIn=expiration
            )
            
            logger.info("Presigned upload URL generated", key=key, expiration=expiration)
            return url
            
        except ClientError as e:
            logger.error("S3 presigned upload URL error", error=str(e), key=key)
            raise Exception(f"S3 presigned upload URL error: {str(e)}")
    
    async def delete_file(self, key: str) -> bool:
        """Delete file from S3."""
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info("File deleted successfully", key=key)
            return True
            
        except ClientError as e:
            logger.error("S3 delete error", error=str(e), key=key)
            return False
    
    async def file_exists(self, key: str) -> bool:
        """Check if file exists in S3."""
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=key)
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            logger.error("S3 head object error", error=str(e), key=key)
            return False
    
    async def get_file_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get file metadata from S3."""
        try:
            response = self.client.head_object(Bucket=self.bucket_name, Key=key)
            
            metadata = {
                'size': response.get('ContentLength'),
                'last_modified': response.get('LastModified'),
                'content_type': response.get('ContentType'),
                'metadata': response.get('Metadata', {})
            }
            
            return metadata
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return None
            logger.error("S3 metadata error", error=str(e), key=key)
            return None

