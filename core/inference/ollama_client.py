"""Cliente leve e desacoplado para comunicação com a API local do Ollama.

Utiliza apenas urllib.request e json da biblioteca padrão do Python para
comunicar-se com o serviço Ollama (por padrão http://127.0.0.1:11434),
sem impor dependências externas pesadas no núcleo.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class OllamaClientError(Exception):
    """Exceção base para erros de comunicação com o Ollama."""


class OllamaConnectionError(OllamaClientError):
    """Erro lançado quando não é possível conectar à instância do Ollama."""


class OllamaResponseError(OllamaClientError):
    """Erro lançado quando o Ollama retorna um status de erro HTTP."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(f"Erro {status_code} retornado pelo Ollama: {message}")
        self.status_code = status_code
        self.message = message


@dataclass
class OllamaClient:
    """Cliente para interagir com o servidor de inferência local do Ollama."""

    base_url: str = "http://127.0.0.1:11434"
    timeout_seconds: float = 30.0

    def is_available(self) -> bool:
        """Verifica se o servidor Ollama está em execução e respondendo."""
        try:
            req = urllib.request.Request(f"{self.base_url.rstrip('/')}/", method="HEAD")
            with urllib.request.urlopen(req, timeout=3.0) as response:
                return response.status in (200, 204)
        except Exception:
            return False

    def list_models(self) -> List[Dict[str, Any]]:
        """Retorna a lista de modelos disponíveis localmente no Ollama."""
        result = self._request("GET", "/api/tags")
        return result.get("models", [])

    def generate(
        self,
        model: str,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Envia um prompt para geração de texto sem streaming.

        Args:
            model: Nome do modelo local (ex: 'llama3.2:3b', 'qwen3.5:2b').
            prompt: Texto do prompt a ser processado.
            system: Instrução de sistema opcional.
            options: Parâmetros adicionais (temperature, top_p, etc.).

        Returns:
            Texto gerado pelo modelo.
        """
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system
        if options:
            payload["options"] = options

        result = self._request("POST", "/api/generate", payload)
        return result.get("response", "")

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """Envia mensagens no formato chat (estruturado) sem streaming.

        Args:
            model: Nome do modelo local.
            messages: Lista de mensagens no formato [{'role': 'user', 'content': '...'}].
            options: Parâmetros opcionais de inferência.

        Returns:
            Dicionário com a mensagem de resposta [{'role': 'assistant', 'content': '...'}].
        """
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
        }
        if options:
            payload["options"] = options

        result = self._request("POST", "/api/chat", payload)
        return result.get("message", {"role": "assistant", "content": ""})

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Executa a requisição HTTP para a API REST do Ollama."""
        url = f"{self.base_url.rstrip('/')}{endpoint}"
        headers = {"Content-Type": "application/json"}
        body = json.dumps(data).encode("utf-8") if data is not None else None

        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                response_bytes = response.read()
                if not response_bytes:
                    return {}
                return json.loads(response_bytes.decode("utf-8"))
        except urllib.error.HTTPError as exc:
            error_msg = exc.read().decode("utf-8", errors="replace")
            raise OllamaResponseError(exc.code, error_msg) from exc
        except (urllib.error.URLError, TimeoutError, ConnectionRefusedError) as exc:
            raise OllamaConnectionError(
                f"Não foi possível conectar ao Ollama em '{url}': {exc}"
            ) from exc

