import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.inference import OllamaClient, OllamaConnectionError
from core.interpretation import (
    MessageIntentCategory,
    MessageInterpretation,
    MessageTone,
    OllamaMessageInterpreter,
    ReceivedMessage,
    RuleBasedMessageInterpreter,
)


class TestOllamaMessageInterpreter(unittest.TestCase):
    """Testes unitários isolados do OllamaMessageInterpreter."""

    def setUp(self):
        self.mock_client = MagicMock(spec=OllamaClient)
        self.interpreter = OllamaMessageInterpreter(
            client=self.mock_client,
            model="llama3.2:3b",
        )

    def test_successful_ollama_interpretation(self):
        mock_output = json.dumps({
            "category": "invitation",
            "description": "Convite para almoço",
            "confidence": 0.95,
            "tones": ["casual", "affectionate"],
            "urgency_level": 2,
            "topics": ["almoço", "encontro"],
            "requires_response": True,
            "signals": [
                {
                    "content": "Amanhã ao meio-dia",
                    "signal_type": "temporal_reference",
                    "confidence": 0.8,
                }
            ],
            "summary": "Convite amigável para almoçar amanhã.",
        })
        self.mock_client.generate.return_value = mock_output

        msg = ReceivedMessage(
            content="Oi amigo! Topa almoçar amanhã ao meio-dia?",
            sender_id="carlos_123",
        )
        result = self.interpreter.interpret(msg)

        self.assertEqual(result.intent.category, MessageIntentCategory.INVITATION)
        self.assertEqual(result.intent.description, "Convite para almoço")
        self.assertIn(MessageTone.CASUAL, result.tones)
        self.assertIn(MessageTone.AFFECTIONATE, result.tones)
        self.assertEqual(result.urgency_level, 2)
        self.assertEqual(result.topics, ["almoço", "encontro"])
        self.assertTrue(result.requires_response)
        self.assertEqual(len(result.signals), 1)
        self.assertTrue(result.signals[0].is_inference)
        self.assertEqual(result.summary, "Convite amigável para almoçar amanhã.")

    def test_parses_json_wrapped_in_markdown(self):
        raw_markdown = """Aqui está a análise:
```json
{
  "category": "question",
  "description": "Dúvida sobre arquivo",
  "confidence": 0.9,
  "tones": ["formal"],
  "urgency_level": 3,
  "topics": ["relatório"],
  "requires_response": true,
  "signals": []
}
```
Espero ter ajudado!"""
        self.mock_client.generate.return_value = raw_markdown

        msg = ReceivedMessage(content="Prezado, onde está o arquivo?", sender_id="chefe")
        result = self.interpreter.interpret(msg)

        self.assertEqual(result.intent.category, MessageIntentCategory.QUESTION)
        self.assertIn(MessageTone.FORMAL, result.tones)
        self.assertEqual(result.urgency_level, 3)

    def test_fallback_on_connection_error(self):
        self.mock_client.generate.side_effect = OllamaConnectionError("Servidor offline")

        msg = ReceivedMessage(
            content="Olá, tudo bem? Podemos conversar?",
            sender_id="contato_456",
        )
        result = self.interpreter.interpret(msg)

        # Fallback (RuleBasedMessageInterpreter) deve responder normalmente
        self.assertIsInstance(result, MessageInterpretation)
        self.assertEqual(result.intent.category, MessageIntentCategory.QUESTION)
        self.assertTrue(result.requires_response)

    def test_fallback_on_invalid_json(self):
        self.mock_client.generate.return_value = "Não é um JSON válido"

        msg = ReceivedMessage(content="Obrigado pela ajuda!", sender_id="contato_789")
        result = self.interpreter.interpret(msg)

        self.assertEqual(result.intent.category, MessageIntentCategory.ACKNOWLEDGMENT)
        self.assertFalse(result.requires_response)


if __name__ == "__main__":
    unittest.main()

