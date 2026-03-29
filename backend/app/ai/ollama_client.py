"""
ollama_client.py
Client untuk berkomunikasi dengan Ollama (model AI lokal).
Mendukung: generate teks, streaming response, cek status model.
"""
import json
import logging
from typing import AsyncGenerator, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Wrapper HTTP untuk Ollama REST API.
    Dokumentasi Ollama API: https://github.com/ollama/ollama/blob/main/docs/api.md
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 120,
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL_NAME
        self.timeout = timeout

    # ── Health Check ─────────────────────────────────────────────────────────

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

    # ── Generate (non-streaming) ─────────────────────────────────────────────

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.6,
        top_p: float = 0.9,
        max_tokens: int = 1024,
    ) -> str:
        """
        Mengirim prompt ke Ollama dan mengembalikan teks lengkap.
        Gunakan ini untuk generate laporan (tidak perlu streaming).
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": max_tokens,
            },
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
                data = resp.json()
                return data.get("response", "").strip()
        except httpx.TimeoutException:
            logger.error("Ollama timeout saat generate")
            raise RuntimeError("Model AI timeout. Coba lagi atau periksa Ollama.")
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP error: {e.response.status_code}")
            raise RuntimeError(f"Ollama error: {e.response.text}")
        except Exception as e:
            logger.error(f"Ollama generate gagal: {e}")
            raise RuntimeError(f"Gagal terhubung ke model AI: {str(e)}")

    # ── Streaming Generate ───────────────────────────────────────────────────

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.6,
        top_p: float = 0.9,
        max_tokens: int = 1024,
    ) -> AsyncGenerator[str, None]:
        """
        Streaming versi: yield potongan teks saat model sedang generate.
        Cocok untuk tampilkan di UI secara real-time.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
                "top_p": top_p,
                "num_predict": max_tokens,
            },
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.strip():
                        chunk = json.loads(line)
                        token = chunk.get("response", "")
                        if token:
                            yield token
                        if chunk.get("done"):
                            break

    # ── Chat (multi-turn) ────────────────────────────────────────────────────

    async def chat(
        self,
        messages: list,
        temperature: float = 0.6,
        max_tokens: int = 1024,
    ) -> str:
        """
        Chat API Ollama (mendukung multi-turn conversation).
        messages format: [{"role": "user"/"assistant", "content": "..."}]
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(f"{self.base_url}/api/chat", json=payload)
            resp.raise_for_status()
            return resp.json()["message"]["content"].strip()


# ── Singleton instances ───────────────────────────────────────────────────────

narrative_client = OllamaClient(model=settings.OLLAMA_MODEL_NAME)
planner_client   = OllamaClient(model=settings.PLANNER_MODEL_NAME)
