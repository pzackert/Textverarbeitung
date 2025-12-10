import httpx
import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001/api/v1")

class APIClient:
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.timeout = httpx.Timeout(
            connect=5.0,
            read=120.0,  # LLM kann lange dauern
            write=30.0,
            pool=5.0
        )

    async def _get(self, endpoint: str, timeout: Optional[float] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        # Use instance timeout if not provided
        req_timeout = timeout if timeout else self.timeout
        async with httpx.AsyncClient(timeout=req_timeout) as client:
            try:
                response = await client.get(url)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"API Error GET {endpoint}: {e.response.text}")
                raise Exception(f"API Error: {e.response.status_code} - {e.response.text}")
            except httpx.RequestError as e:
                logger.error(f"Connection Error GET {endpoint}: {e}")
                raise Exception(f"Connection Error: {str(e)}")

    async def _post(self, endpoint: str, json: Optional[Dict] = None, files: Optional[Dict] = None, timeout: Optional[float] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        req_timeout = timeout if timeout else self.timeout
        async with httpx.AsyncClient(timeout=req_timeout) as client:
            try:
                if files:
                    response = await client.post(url, files=files)
                else:
                    response = await client.post(url, json=json)
                
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"API Error POST {endpoint}: {e.response.text}")
                raise Exception(f"API Error: {e.response.status_code} - {e.response.text}")
            except httpx.RequestError as e:
                logger.error(f"Connection Error POST {endpoint}: {e}")
                raise Exception(f"Connection Error: {str(e)}")

    async def get_system_health(self) -> Dict[str, Any]:
        return await self._get("/system/health")

    async def get_system_stats(self) -> Dict[str, Any]:
        return await self._get("/system/stats")

    async def upload_document(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        filename = os.path.basename(file_path)
        # Determine content type based on extension
        ext = os.path.splitext(filename)[1].lower()
        content_type = "application/octet-stream"
        if ext == ".pdf":
            content_type = "application/pdf"
        elif ext == ".docx":
            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif ext == ".xlsx":
            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        with open(file_path, "rb") as f:
            files = {"file": (filename, f, content_type)}
            return await self._post("/ingest/upload", files=files)

    async def query_rag(self, question: str, template_type: str = "standard", top_k: int = 5, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        payload = {
            "question": question,
            "template_type": template_type,
            "top_k": top_k
        }
        if system_prompt:
            payload["system_prompt"] = system_prompt
        return await self._post("/query", json=payload)

# Singleton instance
api_client = APIClient()
