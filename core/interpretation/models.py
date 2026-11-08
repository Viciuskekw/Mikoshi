"""Modelos de dados para representação e interpretação de mensagens recebidas.

Este módulo define a estrutura de dados mínima e estritamente tipada
para capturar a intenção, tom, contexto e sinais de uma mensagem
recebida pelo usuário do Mikoshi, em conformidade com as diretrizes
de inteligência contextual e separação de fatos/inferências do AGENTS.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class MessageTone(str, Enum):
    """Tons percebidos em uma mensagem recebida."""

    NEUTRAL = "neutral"
    FORMAL = "formal"
    CASUAL = "casual"
    AFFECTIONATE = "affectionate"
    URGENT = "urgent"
    IRRITATED = "irritated"
    IRONIC = "ironic"
    PLAYFUL = "playful"
    ANXIOUS = "anxious"
    CONFUSED = "confused"


class MessageIntentCategory(str, Enum):
    """Categorias principais de intenção da mensagem."""

    GREETING = "greeting"
    QUESTION = "question"
    INVITATION = "invitation"
    REQUEST = "request"
    DEMAND = "demand"
    INFORMATIONAL = "informational"
    EMOTIONAL_SHARING = "emotional_sharing"
    ACKNOWLEDGMENT = "acknowledgment"
    FAREWELL = "farewell"
    OTHER = "other"


@dataclass(frozen=True)
class MessageIntent:
    """Intenção identificada na mensagem recebida."""

    category: MessageIntentCategory
    description: str = ""
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(
                f"confidence deve estar no intervalo [0.0, 1.0], recebido: {self.confidence}"
            )


@dataclass(frozen=True)
class ContextSignal:
    """Sinal contextual extraído de uma mensagem (entidade, evento ou hipótese).

    Em conformidade com a Seção 6.2 do AGENTS.md, hipóteses e inferências
    nunca devem ser tratadas como fatos confirmados sem validação do usuário.
    """

    content: str
    signal_type: str = "general"
    is_inference: bool = True
    confidence: float = 1.0

    def __post_init__(self) -> None:
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(
                f"confidence deve estar no intervalo [0.0, 1.0], recebido: {self.confidence}"
            )


@dataclass(frozen=True)
class ReceivedMessage:
    """Representação estruturada de uma mensagem recebida para interpretação."""

    content: str
    sender_id: str
    timestamp: Optional[datetime] = None
    platform: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.content.strip():
            raise ValueError("O conteúdo da mensagem não pode ser vazio.")
        if not self.sender_id.strip():
            raise ValueError("O sender_id da mensagem não pode ser vazio.")


@dataclass
class MessageInterpretation:
    """Consolidação da interpretação de uma mensagem recebida.

    Estrutura que agrega a intenção, os tons detectados, o nível de urgência,
    os tópicos abordados e sinais para futura consulta na memória ou resposta.
    """

    message: ReceivedMessage
    intent: MessageIntent
    tones: List[MessageTone] = field(default_factory=list)
    urgency_level: int = 1
    topics: List[str] = field(default_factory=list)
    requires_response: bool = True
    signals: List[ContextSignal] = field(default_factory=list)
    summary: Optional[str] = None

    def __post_init__(self) -> None:
        if not (1 <= self.urgency_level <= 5):
            raise ValueError(
                f"urgency_level deve estar entre 1 e 5, recebido: {self.urgency_level}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Serializa a interpretação em um dicionário primitivo estruturado."""
        return {
            "message": {
                "content": self.message.content,
                "sender_id": self.message.sender_id,
                "timestamp": (
                    self.message.timestamp.isoformat()
                    if self.message.timestamp
                    else None
                ),
                "platform": self.message.platform,
                "metadata": dict(self.message.metadata),
            },
            "intent": {
                "category": self.intent.category.value,
                "description": self.intent.description,
                "confidence": self.intent.confidence,
            },
            "tones": [tone.value for tone in self.tones],
            "urgency_level": self.urgency_level,
            "topics": list(self.topics),
            "requires_response": self.requires_response,
            "signals": [
                {
                    "content": signal.content,
                    "signal_type": signal.signal_type,
                    "is_inference": signal.is_inference,
                    "confidence": signal.confidence,
                }
                for signal in self.signals
            ],
            "summary": self.summary,
        }

