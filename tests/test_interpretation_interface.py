import sys
import unittest
from abc import ABC
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.interpretation import (
    MessageIntent,
    MessageIntentCategory,
    MessageInterpretation,
    MessageInterpreter,
    ReceivedMessage,
)


class TestInterpretationInterface(unittest.TestCase):
    """Testes focados na interface abstrata MessageInterpreter."""

    def test_interface_is_abstract(self):
        self.assertTrue(issubclass(MessageInterpreter, ABC))

    def test_cannot_instantiate_abstract_interface_directly(self):
        with self.assertRaises(TypeError):
            MessageInterpreter()  # type: ignore[abstract]

    def test_cannot_instantiate_incomplete_subclass(self):
        class IncompleteInterpreter(MessageInterpreter):
            pass

        with self.assertRaises(TypeError):
            IncompleteInterpreter()  # type: ignore[abstract]

    def test_valid_concrete_subclass_execution(self):
        class StubInterpreter(MessageInterpreter):
            def interpret(self, message: ReceivedMessage) -> MessageInterpretation:
                return MessageInterpretation(
                    message=message,
                    intent=MessageIntent(
                        category=MessageIntentCategory.GREETING,
                        description="Saudação inicial",
                    ),
                    requires_response=False,
                )

        interpreter = StubInterpreter()
        msg = ReceivedMessage(content="Bom dia!", sender_id="user_1")
        result = interpreter.interpret(msg)

        self.assertIsInstance(result, MessageInterpretation)
        self.assertEqual(result.intent.category, MessageIntentCategory.GREETING)
        self.assertEqual(result.message.content, "Bom dia!")
        self.assertFalse(result.requires_response)


if __name__ == "__main__":
    unittest.main()

