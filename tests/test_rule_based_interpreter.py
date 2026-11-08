import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.interpretation import (
    MessageIntentCategory,
    MessageInterpretation,
    MessageTone,
    ReceivedMessage,
    RuleBasedMessageInterpreter,
)


class TestRuleBasedMessageInterpreter(unittest.TestCase):
    """Testes focados na implementação RuleBasedMessageInterpreter."""

    def setUp(self):
        self.interpreter = RuleBasedMessageInterpreter()

    def test_detects_greeting(self):
        msg = ReceivedMessage(content="Olá, boa tarde!", sender_id="user1")
        result = self.interpreter.interpret(msg)

        self.assertEqual(result.intent.category, MessageIntentCategory.GREETING)
        self.assertIn(MessageTone.NEUTRAL, result.tones)
        self.assertFalse(result.requires_response)

    def test_detects_question_and_requires_response(self):
        msg = ReceivedMessage(content="Você já terminou o relatório?", sender_id="user2")
        result = self.interpreter.interpret(msg)

        self.assertEqual(result.intent.category, MessageIntentCategory.QUESTION)
        self.assertTrue(result.requires_response)

    def test_detects_invitation_with_temporal_signal(self):
        msg = ReceivedMessage(content="Bora almoçar amanhã?", sender_id="user3")
        result = self.interpreter.interpret(msg)

        self.assertEqual(result.intent.category, MessageIntentCategory.INVITATION)
        self.assertTrue(result.requires_response)
        self.assertIn(MessageTone.CASUAL, result.tones)
        # Sinais temporais
        self.assertTrue(any("amanhã" in s.content for s in result.signals))
        for signal in result.signals:
            self.assertTrue(signal.is_inference)

    def test_detects_urgency_and_tone(self):
        msg = ReceivedMessage(content="Preciso disso urgente agora!", sender_id="user4")
        result = self.interpreter.interpret(msg)

        self.assertIn(MessageTone.URGENT, result.tones)
        self.assertGreaterEqual(result.urgency_level, 3)
        self.assertEqual(result.intent.category, MessageIntentCategory.DEMAND)

    def test_detects_acknowledgment(self):
        msg = ReceivedMessage(content="Muito obrigado pela ajuda!", sender_id="user5")
        result = self.interpreter.interpret(msg)

        self.assertEqual(result.intent.category, MessageIntentCategory.ACKNOWLEDGMENT)
        self.assertFalse(result.requires_response)


if __name__ == "__main__":
    unittest.main()

