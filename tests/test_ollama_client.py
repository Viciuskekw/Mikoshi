import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.inference import (
    OllamaClient,
    OllamaClientError,
    OllamaConnectionError,
    OllamaResponseError,
)


class TestOllamaClient(unittest.TestCase):
    """Testes unitários isolados do OllamaClient com mocks HTTP."""

    def setUp(self):
        self.client = OllamaClient(base_url="http://127.0.0.1:11434", timeout_seconds=5.0)

    @patch("urllib.request.urlopen")
    def test_is_available_true(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        self.assertTrue(self.client.is_available())

    @patch("urllib.request.urlopen")
    def test_is_available_false_on_connection_error(self, mock_urlopen):
        mock_urlopen.side_effect = ConnectionRefusedError("Connection refused")

        self.assertFalse(self.client.is_available())

    @patch("urllib.request.urlopen")
    def test_list_models_success(self, mock_urlopen):
        fake_data = {"models": [{"name": "llama3.2:3b"}, {"name": "qwen3.5:2b"}]}
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(fake_data).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        models = self.client.list_models()
        self.assertEqual(len(models), 2)
        self.assertEqual(models[0]["name"], "llama3.2:3b")

    @patch("urllib.request.urlopen")
    def test_generate_success(self, mock_urlopen):
        fake_response = {"response": "Olá! Como posso ajudar você?"}
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(fake_response).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        result = self.client.generate(model="llama3.2:3b", prompt="Olá")
        self.assertEqual(result, "Olá! Como posso ajudar você?")

    @patch("urllib.request.urlopen")
    def test_chat_success(self, mock_urlopen):
        fake_message = {"role": "assistant", "content": "Tudo ótimo por aqui!"}
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"message": fake_message}).encode("utf-8")
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        res = self.client.chat(
            model="llama3.2:3b",
            messages=[{"role": "user", "content": "Como você está?"}],
        )
        self.assertEqual(res["content"], "Tudo ótimo por aqui!")

    @patch("urllib.request.urlopen")
    def test_connection_error_raises_ollama_connection_error(self, mock_urlopen):
        import urllib.error
        mock_urlopen.side_effect = urllib.error.URLError("Server unreachable")

        with self.assertRaises(OllamaConnectionError):
            self.client.list_models()


if __name__ == "__main__":
    unittest.main()

