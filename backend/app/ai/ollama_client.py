"""
ollama_client.py
Client untuk berkomunikasi dengan Ollama (model AI lokal).
"""
import json
import logging
from typing import Optional
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 600,
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL_NAME
        self.timeout = timeout

    async def is_available(self) -> bool:
        """Cek apakah Ollama service berjalan dan model tersedia."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code != 200:
                    return False
                models = [m["name"] for m in resp.json().get("models", [])]
                return any(self.model in m for m in models)
        except Exception as e:
            logger.warning(f"Ollama tidak tersedia: {e}")
            return False

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        num_predict: int = 2048, # Default ditingkatkan untuk laporan panjang
    ) -> str:
        """
        Mengirim prompt ke Ollama. 
        Menggunakan 'options' untuk num_predict sesuai spek API Ollama.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json", # Memaksa output JSON sesuai Modelfile Sania
            "options": {
                "num_predict": num_predict,
                "temperature": 0.7,
                "top_p": 0.9
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                resp.raise_for_status()
                # Menggunakan resp.json() yang lebih aman
                data = resp.json()
                return data.get("response", "").strip()
        except httpx.TimeoutException:
            logger.error("Ollama timeout saat generate")
            raise RuntimeError("Model AI timeout. Coba lagi atau periksa Ollama.")
        except Exception as e:
            logger.error(f"Ollama generate gagal: {e}")
            raise RuntimeError(f"Gagal terhubung ke model AI: {str(e)}")

# Singleton instance
narrative_client = OllamaClient(model=settings.OLLAMA_MODEL_NAME)