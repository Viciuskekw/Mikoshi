"""Módulo de interpretação de mensagens recebidas."""

from core.interpretation.interface import MessageInterpreter
from core.interpretation.models import (
    ContextSignal,
    MessageIntent,
    MessageIntentCategory,
    MessageInterpretation,
    MessageTone,
    ReceivedMessage,
)
from core.interpretation.rule_based import RuleBasedMessageInterpreter

__all__ = [
    "ContextSignal",
    "MessageIntent",
    "MessageIntentCategory",
    "MessageInterpretation",
    "MessageInterpreter",
    "MessageTone",
    "ReceivedMessage",
    "RuleBasedMessageInterpreter",
]
