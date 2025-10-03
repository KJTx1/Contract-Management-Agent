"""OCI Object Storage integration for document storage."""

import os
import uuid
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

import oci
from oci.object_storage import ObjectStorageClient
from oci.exceptions import ServiceError
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)


class OCIStorage:
    """OCI Object Storage client for document management."""
    
    # Class constants
    REQUIRED_CONFIG_PARAMS = ["user", "fingerprint", "key_file", "tenancy", "region"]
    DEFAULT_CONFIG_FILE = "~/.oci/config"
    DEFAULT_PROFILE = "DEFAULT"
    DEFAULT_CONTENT_TYPE = "application/pdf"
    DEFAULT_PREFIX = "documents/"
    
    def __init__(self):
        """Initialize OCI Object Storage client."""
        # Load environment variables from .env file
        load_dotenv()
        
        self.config = self._load_config()
        self.client = None
        self.bucket_name = os.getenv("OCI_BUCKET_NAME")
        self.bucket_id = os.getenv("OCI_BUCKET_ID")
        self.namespace = None
        self._thread_pool = None
        
        if self.config:
            self.client = ObjectStorageClient(self.config)
            self._get_namespace()
            self._validate_environment()
    
    def _load_config(self) -> Optional[Dict[str, Any]]:
        """Load OCI configuration from file or environment variables."""
        try:
            config_file = os.getenv("OCI_CONFIG_FILE", self.DEFAULT_CONFIG_FILE)
            profile = os.getenv("OCI_PROFILE", self.DEFAULT_PROFILE)
            
            if os.path.exists(os.path.expanduser(config_file)):
                logger.info(f"Loading OCI config from file: {config_file}")
                config = oci.config.from_file(config_file, profile)
                return self._validate_config(config)
            else:
                logger.info("Loading OCI config from environment variables")
                return self._load_from_env()
                
        except Exception as e:
            logger.error(f"Failed to load OCI configuration: {e}")
            return None
    
    def _load_from_env(self) -> Optional[Dict[str, Any]]:
        """Load OCI configuration from environment variables."""
        config_dict = {
            "user": os.getenv("OCI_USER_OCID"),
            "fingerprint": os.getenv("OCI_FINGERPRINT"),
            "key_file": os.getenv("OCI_KEY_FILE"),
            "tenancy": os.getenv("OCI_TENANCY_OCID"),
            "region": os.getenv("OCI_REGION"),
            "pass_phrase": os.getenv("OCI_KEY_PASSPHRASE")
        }
        
        return self._validate_config(config_dict)
    
    def _validate_config(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validate OCI configuration parameters."""
        missing_params = [
            param for param in self.REQUIRED_CONFIG_PARAMS 
            if not config.get(param)
        ]
        
        if missing_params:
            logger.warning(f"Missing OCI configuration parameters: {missing_params}")
            return None
        
        return config
    
    def _validate_environment(self):
        """Validate required environment variables."""
        if not self.bucket_name:
            logger.warning("OCI_BUCKET_NAME not set in environment")
        if not self.bucket_id:
            logger.warning("OCI_BUCKET_ID not set in environment")
    
    def _get_namespace(self):
        """Get the object storage namespace."""
        if not self.client:
            return
        
        try:
            response = self.client.get_namespace()
            self.namespace = response.data
            logger.info(f"OCI namespace: {self.namespace}")
        except ServiceError as e:
            logger.error(f"Error getting OCI namespace: {e}")
            self.namespace = None
    
    @lru_cache(maxsize=1)
    def _get_thread_pool(self) -> ThreadPoolExecutor:
        """Get or create thread pool executor."""
        if self._thread_pool is None:
            self._thread_pool = ThreadPoolExecutor(max_workers=4)
        return self._thread_pool
    
    def _parse_object_url(self, object_url: str) -> Optional[Tuple[str, str, str]]:
        """Parse OCI object URL into namespace, bucket, and object name."""
        if not object_url.startswith("oci://"):
            logger.error(f"Invalid OCI object URL: {object_url}")
            return None
        
        parts = object_url[6:].split("/", 2)  # Remove "oci://" prefix
        if len(parts) != 3:
            logger.error(f"Invalid OCI object URL format: {object_url}")
            return None
        
        return tuple(parts)
    
    def _create_object_url(self, object_name: str) -> str:
        """Create OCI object URL from object name."""
        return f"oci://{self.namespace}/{self.bucket_name}/{object_name}"
    
    async def _run_in_thread_pool(self, func, *args, **kwargs):
        """Run function in thread pool to avoid blocking."""
        loop = asyncio.get_event_loop()
        executor = self._get_thread_pool()
        return await loop.run_in_executor(executor, func, *args, **kwargs)
    
    def is_available(self) -> bool:
        """Check if OCI storage is available."""
        return self.client is not None and self.namespace is not None
    
    async def upload_document(
        self, 
        file_path: str, 
        content_type: str = DEFAULT_CONTENT_TYPE,
        object_name: Optional[str] = None
    ) -> Optional[str]:
        """Upload a document to OCI Object Storage."""
        if not self.is_available():
            logger.error("OCI storage not available")
            return None
        
        try:
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                logger.error(f"File not found: {file_path}")
                return None
            
            # Generate object name if not provided
            if not object_name:
                file_name = file_path_obj.name
                object_name = f"{self.DEFAULT_PREFIX}{uuid.uuid4()}_{file_name}"
            
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Upload to OCI
            def _upload():
                return self.client.put_object(
                    namespace_name=self.namespace,
                    bucket_name=self.bucket_name,
                    object_name=object_name,
                    content_type=content_type,
                    put_object_body=file_content
                )
            
            await self._run_in_thread_pool(_upload)
            
            # Return the object URL
            object_url = self._create_object_url(object_name)
            logger.info(f"Uploaded document to OCI: {object_url}")
            return object_url
            
        except Exception as e:
            logger.error(f"Error uploading document to OCI: {e}")
            return None
    
    async def download_document(self, object_url: str) -> Optional[bytes]:
        """Download a document from OCI Object Storage."""
        if not self.is_available():
            logger.error("OCI storage not available")
            return None
        
        try:
            parsed_url = self._parse_object_url(object_url)
            if not parsed_url:
                return None
            
            namespace, bucket, object_name = parsed_url
            
            # Download from OCI
            def _download():
                return self.client.get_object(namespace, bucket, object_name)
            
            response = await self._run_in_thread_pool(_download)
            return response.data.content
            
        except Exception as e:
            logger.error(f"Error downloading document from OCI: {e}")
            return None
    
    async def delete_document(self, object_url: str) -> bool:
        """Delete a document from OCI Object Storage."""
        if not self.is_available():
            logger.error("OCI storage not available")
            return False
        
        try:
            parsed_url = self._parse_object_url(object_url)
            if not parsed_url:
                return False
            
            namespace, bucket, object_name = parsed_url
            
            # Delete from OCI
            def _delete():
                return self.client.delete_object(namespace, bucket, object_name)
            
            await self._run_in_thread_pool(_delete)
            logger.info(f"Deleted document from OCI: {object_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document from OCI: {e}")
            return False
    
    async def list_documents(self, prefix: str = DEFAULT_PREFIX) -> List[Dict[str, Any]]:
        """List documents in OCI Object Storage."""
        if not self.is_available():
            logger.error("OCI storage not available")
            return []
        
        try:
            def _list():
                return self.client.list_objects(
                    namespace_name=self.namespace,
                    bucket_name=self.bucket_name,
                    prefix=prefix
                )
            
            response = await self._run_in_thread_pool(_list)
            
            documents = []
            for obj in response.data.objects:
                documents.append({
                    "name": obj.name,
                    "size": obj.size,
                    "etag": obj.etag,
                    "time_created": obj.time_created,
                    "url": self._create_object_url(obj.name)
                })
            
            logger.info(f"Listed {len(documents)} documents with prefix: {prefix}")
            return documents
            
        except Exception as e:
            logger.error(f"Error listing documents from OCI: {e}")
            return []
    
    async def get_document_info(self, object_url: str) -> Optional[Dict[str, Any]]:
        """Get document metadata from OCI Object Storage."""
        if not self.is_available():
            logger.error("OCI storage not available")
            return None
        
        try:
            parsed_url = self._parse_object_url(object_url)
            if not parsed_url:
                return None
            
            namespace, bucket, object_name = parsed_url
            
            def _get_info():
                return self.client.head_object(namespace, bucket, object_name)
            
            response = await self._run_in_thread_pool(_get_info)
            
            return {
                "name": object_name,
                "size": response.headers.get("content-length"),
                "content_type": response.headers.get("content-type"),
                "etag": response.headers.get("etag"),
                "last_modified": response.headers.get("last-modified"),
                "url": object_url
            }
            
        except Exception as e:
            logger.error(f"Error getting document info from OCI: {e}")
            return None
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage configuration information."""
        return {
            "available": self.is_available(),
            "bucket_name": self.bucket_name,
            "bucket_id": self.bucket_id,
            "namespace": self.namespace,
            "config_loaded": self.config is not None
        }
    
    async def close(self):
        """Close the OCI storage client and cleanup resources."""
        if self._thread_pool:
            self._thread_pool.shutdown(wait=True)
            self._thread_pool = None
        logger.info("OCI storage client closed")
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        if self._thread_pool:
            self._thread_pool.shutdown(wait=False)