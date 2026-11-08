"""Interpretador de mensagens recebidas baseado em modelo local via Ollama.

Implementa MessageInterpreter utilizando prompts estruturados (JSON) direcionados
ao Ollama, com suporte a fallback automático para RuleBasedMessageInterpreter
caso o serviço local esteja inacessível ou ocorra falha na decodificação da resposta.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from core.inference.ollama_client import OllamaClient, OllamaClientError
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

_SYSTEM_PROMPT = """Você é o subsistema de análise contextual e interpretação do assistente Mikoshi.
Sua função é estritamente analisar a mensagem recebida e emitir um JSON válido com a interpretação.
Não converse nem adicione texto fora do JSON.

Formato esperado:
{
  "category": "greeting|question|invitation|request|demand|informational|emotional_sharing|acknowledgment|farewell|other",
  "description": "descrição concisa da intenção",
  "confidence": 0.0 a 1.0,
  "tones": ["neutral", "casual", "formal", "affectionate", "urgent", "irritated", "ironic", "playful", "anxious", "confused"],
  "urgency_level": 1 a 5,
  "topics": ["tópico1", "tópico2"],
  "requires_response": true/false,
  "signals": [
    {
      "content": "descrição do sinal ou referência",
      "signal_type": "temporal_reference|topic_link|entity|hypothesis",
      "confidence": 0.0 a 1.0
    }
  ],
  "summary": "resumo conciso da mensagem"
}
"""


class OllamaMessageInterpreter(MessageInterpreter):
    """Interpretador baseado em LLM local via Ollama com fallback seguro."""

    def __init__(
        self,
        client: Optional[OllamaClient] = None,
        model: str = "llama3.2:3b",
        fallback_interpreter: Optional[MessageInterpreter] = None,
    ) -> None:
        self.client = client or OllamaClient()
        self.model = model
        self.fallback = fallback_interpreter or RuleBasedMessageInterpreter()

    def interpret(self, message: ReceivedMessage) -> MessageInterpretation:
        """Interpreta a mensagem via Ollama; em caso de falha, aciona o fallback."""
        try:
            return self._interpret_with_ollama(message)
        except (OllamaClientError, json.JSONDecodeError, KeyError, ValueError):
            return self.fallback.interpret(message)

    def _interpret_with_ollama(self, message: ReceivedMessage) -> MessageInterpretation:
        prompt = (
            f"Remetente: {message.sender_id}\n"
            f"Plataforma: {message.platform or 'desconhecida'}\n"
            f"Mensagem recebida:\n\"\"\"{message.content}\"\"\"\n"
            "Retorne apenas o JSON de análise:"
        )

        raw_response = self.client.generate(
            model=self.model,
            prompt=prompt,
            system=_SYSTEM_PROMPT,
            options={"temperature": 0.1},
        )

        parsed_data = self._parse_json_response(raw_response)
        return self._build_interpretation(message, parsed_data)

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Extrai e decodifica o JSON mesmo se vier envolvido em blocos markdown."""
        cleaned = text.strip()
        json_match = re.search(r"\{.*\}", cleaned, re.DOTALL)
        if json_match:
            cleaned = json_match.group(0)
        return json.loads(cleaned)

    def _build_interpretation(
        self, message: ReceivedMessage, data: Dict[str, Any]
    ) -> MessageInterpretation:
        # 1. Categoria da intenção
        cat_str = str(data.get("category", "other")).lower()
        try:
            category = MessageIntentCategory(cat_str)
        except ValueError:
            category = MessageIntentCategory.OTHER

        confidence = float(data.get("confidence", 0.8))
        confidence = max(0.0, min(1.0, confidence))

        intent = MessageIntent(
            category=category,
            description=str(data.get("description", "")),
            confidence=confidence,
        )

        # 2. Tons
        raw_tones = data.get("tones", [])
        tones: List[MessageTone] = []
        for t in raw_tones:
            try:
                tones.append(MessageTone(str(t).lower()))
            except ValueError:
                continue
        if not tones:
            tones.append(MessageTone.NEUTRAL)

        # 3. Urgência
        raw_urgency = int(data.get("urgency_level", 1))
        urgency = max(1, min(5, raw_urgency))

        # 4. Tópicos
        topics = [str(t) for t in data.get("topics", []) if isinstance(t, str)]

        # 5. Requer resposta
        requires_response = bool(data.get("requires_response", True))

        # 6. Sinais (sempre definidos como inferências - AGENTS.md Seção 6.2)
        signals: List[ContextSignal] = []
        for item in data.get("signals", []):
            if isinstance(item, dict) and "content" in item:
                sig_conf = float(item.get("confidence", 0.7))
                signals.append(
                    ContextSignal(
                        content=str(item["content"]),
                        signal_type=str(item.get("signal_type", "hypothesis")),
                        is_inference=True,
                        confidence=max(0.0, min(1.0, sig_conf)),
                    )
                )

        summary = data.get("summary")
        if summary is not None:
            summary = str(summary)

        return MessageInterpretation(
            message=message,
            intent=intent,
            tones=tones,
            urgency_level=urgency,
            topics=topics,
            requires_response=requires_response,
            signals=signals,
            summary=summary,
        )

