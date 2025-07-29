"""
AWS S3 Service for ClimateCoach
Handles file uploads, logs, and data storage in S3
"""

import boto3
import os
import logging
from datetime import datetime
from typing import Optional, Dict, List
import json
from botocore.exceptions import ClientError, NoCredentialsError
import gzip
import io

logger = logging.getLogger(__name__)

class S3Service:
    """
    Service for managing files and logs in AWS S3
    """
    
    def __init__(self, aws_access_key_id: Optional[str] = None, 
                 aws_secret_access_key: Optional[str] = None,
                 bucket_name: Optional[str] = None,
                 region_name: str = 'us-east-1'):
        """
        Initialize S3 service
        """
        self.aws_access_key_id = aws_access_key_id or os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = aws_secret_access_key or os.getenv('AWS_SECRET_ACCESS_KEY')
        self.bucket_name = bucket_name or os.getenv('AWS_S3_BUCKET', 'climatecoach-global')
        self.region_name = region_name
        
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            )
            self.s3_resource = boto3.resource(
                's3',
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            )
            
            # Test connection
            self._test_connection()
            logger.info(f"S3 service initialized successfully for bucket: {self.bucket_name}")
            
        except NoCredentialsError:
            logger.error("AWS credentials not found. S3 service will not be available.")
            self.s3_client = None
            self.s3_resource = None
        except Exception as e:
            logger.error(f"Failed to initialize S3 service: {e}")
            self.s3_client = None
            self.s3_resource = None
    
    def _test_connection(self):
        """Test S3 connection"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                logger.info(f"Bucket {self.bucket_name} does not exist. Creating...")
                self._create_bucket()
            else:
                raise e
    
    def _create_bucket(self):
        """Create S3 bucket if it doesn't exist"""
        try:
            if self.region_name == 'us-east-1':
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region_name}
                )
            
            # Set bucket policy for climate data sharing
            self._set_bucket_policy()
            logger.info(f"Created S3 bucket: {self.bucket_name}")
            
        except ClientError as e:
            logger.error(f"Failed to create bucket {self.bucket_name}: {e}")
            raise
    
    def _set_bucket_policy(self):
        """Set bucket policy for appropriate access"""
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "ClimateCoachAccess",
                    "Effect": "Allow",
                    "Principal": {"AWS": f"arn:aws:iam::{self._get_account_id()}:root"},
                    "Action": [
                        "s3:GetObject",
                        "s3:PutObject",
                        "s3:DeleteObject"
                    ],
                    "Resource": f"arn:aws:s3:::{self.bucket_name}/*"
                }
            ]
        }
        
        try:
            self.s3_client.put_bucket_policy(
                Bucket=self.bucket_name,
                Policy=json.dumps(bucket_policy)
            )
        except ClientError as e:
            logger.warning(f"Could not set bucket policy: {e}")
    
    def _get_account_id(self) -> str:
        """Get AWS account ID"""
        try:
            sts = boto3.client('sts', 
                             aws_access_key_id=self.aws_access_key_id,
                             aws_secret_access_key=self.aws_secret_access_key)
            return sts.get_caller_identity()['Account']
        except:
            return "*"  # Fallback
    
    def upload_file(self, file_path: str, s3_key: str, 
                   metadata: Optional[Dict] = None) -> bool:
        """
        Upload a file to S3
        """
        if not self.s3_client:
            logger.error("S3 client not available")
            return False
        
        try:
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.s3_client.upload_file(
                file_path, 
                self.bucket_name, 
                s3_key,
                ExtraArgs=extra_args
            )
            
            logger.info(f"Successfully uploaded {file_path} to s3://{self.bucket_name}/{s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to upload {file_path}: {e}")
            return False
    
    def upload_data(self, data: bytes, s3_key: str, 
                   content_type: str = 'application/octet-stream',
                   metadata: Optional[Dict] = None) -> bool:
        """
        Upload data directly to S3
        """
        if not self.s3_client:
            logger.error("S3 client not available")
            return False
        
        try:
            extra_args = {'ContentType': content_type}
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=data,
                **extra_args
            )
            
            logger.info(f"Successfully uploaded data to s3://{self.bucket_name}/{s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Failed to upload data to {s3_key}: {e}")
            return False
    
    def upload_log(self, log_data: str, log_type: str = 'application',
                  compress: bool = True) -> bool:
        """
        Upload log data to S3 with timestamp
        """
        timestamp = datetime.utcnow().strftime('%Y/%m/%d/%H')
        log_key = f"logs/{log_type}/{timestamp}/{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.log"
        
        if compress:
            log_key += ".gz"
            # Compress log data
            buffer = io.BytesIO()
            with gzip.GzipFile(fileobj=buffer, mode='wb') as gz:
                gz.write(log_data.encode('utf-8'))
            compressed_data = buffer.getvalue()
            
            return self.upload_data(
                compressed_data, 
                log_key,
                content_type='application/gzip',
                metadata={
                    'log_type': log_type,
                    'timestamp': datetime.utcnow().isoformat(),
                    'compressed': 'true'
                }
            )
        else:
            return self.upload_data(
                log_data.encode('utf-8'),
                log_key,
                content_type='text/plain',
                metadata={
                    'log_type': log_type,
                    'timestamp': datetime.utcnow().isoformat(),
                    'compressed': 'false'
                }
            )
    
    def upload_climate_data(self, climate_data: Dict, location: str,
                           data_type: str = 'daily') -> bool:
        """
        Upload climate data with proper organization
        """
        timestamp = datetime.utcnow()
        date_path = timestamp.strftime('%Y/%m/%d')
        
        # Sanitize location for S3 key
        safe_location = location.replace(' ', '_').replace(',', '_').lower()
        
        data_key = f"climate_data/{data_type}/{safe_location}/{date_path}/{timestamp.strftime('%H%M%S')}.json"
        
        # Add metadata
        enhanced_data = {
            'timestamp': timestamp.isoformat(),
            'location': location,
            'data_type': data_type,
            'data': climate_data
        }
        
        return self.upload_data(
            json.dumps(enhanced_data, indent=2).encode('utf-8'),
            data_key,
            content_type='application/json',
            metadata={
                'location': location,
                'data_type': data_type,
                'timestamp': timestamp.isoformat()
            }
        )
    
    def upload_user_data(self, user_id: str, data: Dict, 
                        data_category: str = 'profile') -> bool:
        """
        Upload user data with privacy considerations
        """
        # Hash user ID for privacy
        import hashlib
        hashed_user_id = hashlib.sha256(user_id.encode()).hexdigest()[:16]
        
        timestamp = datetime.utcnow()
        data_key = f"user_data/{data_category}/{hashed_user_id}/{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        
        # Add timestamp to data
        enhanced_data = {
            'timestamp': timestamp.isoformat(),
            'category': data_category,
            'data': data
        }
        
        return self.upload_data(
            json.dumps(enhanced_data, indent=2).encode('utf-8'),
            data_key,
            content_type='application/json',
            metadata={
                'user_id_hash': hashed_user_id,
                'category': data_category,
                'timestamp': timestamp.isoformat(),
                'privacy_compliant': 'true'
            }
        )
    
    def download_file(self, s3_key: str, local_path: str) -> bool:
        \"\"\"Download file from S3\"\"\"\n        if not self.s3_client:\n            logger.error(\"S3 client not available\")\n            return False\n        \n        try:\n            self.s3_client.download_file(self.bucket_name, s3_key, local_path)\n            logger.info(f\"Downloaded s3://{self.bucket_name}/{s3_key} to {local_path}\")\n            return True\n        except ClientError as e:\n            logger.error(f\"Failed to download {s3_key}: {e}\")\n            return False\n    \n    def get_object_data(self, s3_key: str) -> Optional[bytes]:\n        \"\"\"Get object data from S3\"\"\"\n        if not self.s3_client:\n            logger.error(\"S3 client not available\")\n            return None\n        \n        try:\n            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=s3_key)\n            return response['Body'].read()\n        except ClientError as e:\n            logger.error(f\"Failed to get object {s3_key}: {e}\")\n            return None\n    \n    def list_objects(self, prefix: str = '', max_keys: int = 1000) -> List[Dict]:\n        \"\"\"List objects in S3 bucket\"\"\"\n        if not self.s3_client:\n            logger.error(\"S3 client not available\")\n            return []\n        \n        try:\n            response = self.s3_client.list_objects_v2(\n                Bucket=self.bucket_name,\n                Prefix=prefix,\n                MaxKeys=max_keys\n            )\n            \n            return response.get('Contents', [])\n        except ClientError as e:\n            logger.error(f\"Failed to list objects with prefix {prefix}: {e}\")\n            return []\n    \n    def delete_object(self, s3_key: str) -> bool:\n        \"\"\"Delete object from S3\"\"\"\n        if not self.s3_client:\n            logger.error(\"S3 client not available\")\n            return False\n        \n        try:\n            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)\n            logger.info(f\"Deleted s3://{self.bucket_name}/{s3_key}\")\n            return True\n        except ClientError as e:\n            logger.error(f\"Failed to delete {s3_key}: {e}\")\n            return False\n    \n    def get_presigned_url(self, s3_key: str, expiration: int = 3600) -> Optional[str]:\n        \"\"\"Generate presigned URL for object access\"\"\"\n        if not self.s3_client:\n            logger.error(\"S3 client not available\")\n            return None\n        \n        try:\n            url = self.s3_client.generate_presigned_url(\n                'get_object',\n                Params={'Bucket': self.bucket_name, 'Key': s3_key},\n                ExpiresIn=expiration\n            )\n            return url\n        except ClientError as e:\n            logger.error(f\"Failed to generate presigned URL for {s3_key}: {e}\")\n            return None\n    \n    def create_backup(self, data: Dict, backup_type: str = 'full') -> bool:\n        \"\"\"Create system backup\"\"\"\n        timestamp = datetime.utcnow()\n        backup_key = f\"backups/{backup_type}/{timestamp.strftime('%Y/%m/%d')}/{timestamp.strftime('%Y%m%d_%H%M%S')}.json\"\n        \n        backup_data = {\n            'timestamp': timestamp.isoformat(),\n            'backup_type': backup_type,\n            'version': '1.0',\n            'data': data\n        }\n        \n        # Compress large backups\n        json_data = json.dumps(backup_data, indent=2).encode('utf-8')\n        if len(json_data) > 1024 * 1024:  # 1MB threshold\n            buffer = io.BytesIO()\n            with gzip.GzipFile(fileobj=buffer, mode='wb') as gz:\n                gz.write(json_data)\n            compressed_data = buffer.getvalue()\n            \n            backup_key += '.gz'\n            return self.upload_data(\n                compressed_data,\n                backup_key,\n                content_type='application/gzip',\n                metadata={\n                    'backup_type': backup_type,\n                    'timestamp': timestamp.isoformat(),\n                    'compressed': 'true'\n                }\n            )\n        else:\n            return self.upload_data(\n                json_data,\n                backup_key,\n                content_type='application/json',\n                metadata={\n                    'backup_type': backup_type,\n                    'timestamp': timestamp.isoformat(),\n                    'compressed': 'false'\n                }\n            )\n\n# Example usage\nif __name__ == \"__main__\":\n    s3_service = S3Service()\n    \n    # Test upload\n    test_data = {\n        'message': 'Hello ClimateCoach Global!',\n        'timestamp': datetime.utcnow().isoformat()\n    }\n    \n    success = s3_service.upload_climate_data(\n        test_data, \n        'New York, USA', \n        'test'\n    )\n    \n    print(f\"Upload success: {success}\")
