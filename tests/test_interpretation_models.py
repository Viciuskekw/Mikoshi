import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.interpretation.models import (
    ContextSignal,
    MessageIntent,
    MessageIntentCategory,
    MessageInterpretation,
    MessageTone,
    ReceivedMessage,
)


class TestInterpretationModels(unittest.TestCase):
    """Testes focados nos modelos de dados de interpretação de mensagens."""

    def test_received_message_creation_valid(self):
        msg = ReceivedMessage(
            content="Oi, você vai ao aniversário amanhã?",
            sender_id="contato_123",
            platform="whatsapp",
        )
        self.assertEqual(msg.content, "Oi, você vai ao aniversário amanhã?")
        self.assertEqual(msg.sender_id, "contato_123")
        self.assertEqual(msg.platform, "whatsapp")
        self.assertIsNone(msg.timestamp)
        self.assertEqual(msg.metadata, {})

    def test_received_message_rejects_empty_content_or_sender(self):
        with self.assertRaises(ValueError):
            ReceivedMessage(content="   ", sender_id="contato_123")

        with self.assertRaises(ValueError):
            ReceivedMessage(content="Olá", sender_id="   ")

    def test_message_intent_confidence_bounds(self):
        intent = MessageIntent(
            category=MessageIntentCategory.QUESTION,
            description="Pergunta sobre disponibilidade",
            confidence=0.85,
        )
        self.assertEqual(intent.category, MessageIntentCategory.QUESTION)
        self.assertAlmostEqual(intent.confidence, 0.85)

        with self.assertRaises(ValueError):
            MessageIntent(category=MessageIntentCategory.QUESTION, confidence=1.5)

        with self.assertRaises(ValueError):
            MessageIntent(category=MessageIntentCategory.QUESTION, confidence=-0.1)

    def test_context_signal_defaults_to_inference(self):
        # Conforme AGENTS.md Seção 6.2: Sinais não confirmados devem ser tratados como inferências
        signal = ContextSignal(
            content="Aniversário mencionado",
            signal_type="event",
        )
        self.assertTrue(signal.is_inference)
        self.assertEqual(signal.signal_type, "event")
        self.assertEqual(signal.confidence, 1.0)

        with self.assertRaises(ValueError):
            ContextSignal(content="Algo", confidence=1.1)

    def test_message_interpretation_valid_and_to_dict(self):
        timestamp = datetime(2026, 11, 8, 18, 30, tzinfo=timezone.utc)
        msg = ReceivedMessage(
            content="E aí, tudo bem? Podemos conversar sobre o projeto hoje?",
            sender_id="alice_456",
            timestamp=timestamp,
            platform="telegram",
            metadata={"chat_id": 999},
        )
        intent = MessageIntent(
            category=MessageIntentCategory.REQUEST,
            description="Solicitação para reunião rápida",
            confidence=0.9,
        )
        signal = ContextSignal(
            content="Projeto compartilhado",
            signal_type="topic_link",
            is_inference=True,
            confidence=0.7,
        )
        interpretation = MessageInterpretation(
            message=msg,
            intent=intent,
            tones=[MessageTone.CASUAL, MessageTone.AFFECTIONATE],
            urgency_level=2,
            topics=["projeto", "reunião"],
            requires_response=True,
            signals=[signal],
            summary="Alice pede conversa rápida sobre o projeto.",
        )

        self.assertEqual(interpretation.urgency_level, 2)
        self.assertTrue(interpretation.requires_response)
        self.assertIn(MessageTone.CASUAL, interpretation.tones)

        data = interpretation.to_dict()
        self.assertEqual(data["message"]["sender_id"], "alice_456")
        self.assertEqual(data["message"]["platform"], "telegram")
        self.assertEqual(data["message"]["timestamp"], timestamp.isoformat())
        self.assertEqual(data["intent"]["category"], "request")
        self.assertEqual(data["tones"], ["casual", "affectionate"])
        self.assertEqual(data["urgency_level"], 2)
        self.assertEqual(data["topics"], ["projeto", "reunião"])
        self.assertEqual(data["signals"][0]["content"], "Projeto compartilhado")
        self.assertTrue(data["signals"][0]["is_inference"])

    def test_interpretation_urgency_level_validation(self):
        msg = ReceivedMessage(content="Teste", sender_id="id1")
        intent = MessageIntent(category=MessageIntentCategory.OTHER)

        with self.assertRaises(ValueError):
            MessageInterpretation(message=msg, intent=intent, urgency_level=0)

        with self.assertRaises(ValueError):
            MessageInterpretation(message=msg, intent=intent, urgency_level=6)


if __name__ == "__main__":
    unittest.main()

