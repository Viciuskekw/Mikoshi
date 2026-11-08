"""Interpretador básico baseado em regras e heurísticas textuais.

Fornece uma implementação padrão, leve e determinística de MessageInterpreter,
útil para testes rápidos, ambientes sem GPU e como fallback de segurança
caso o modelo de linguagem local esteja indisponível.
"""

from __future__ import annotations

import re
from typing import List, Set, Tuple

from core.interpretation.interface import MessageInterpreter
from core.interpretation.models import (
    ContextSignal,
    MessageIntent,
    MessageIntentCategory,
    MessageInterpretation,
    MessageTone,
    ReceivedMessage,
)


class RuleBasedMessageInterpreter(MessageInterpreter):
    """Interpretador determinístico de mensagens recebidas baseado em regras."""

    # Padrões comuns para intenções
    _GREETING_PATTERNS = [
        r"\b(ol[aá]|oi|oie|bom dia|boa tarde|boa noite|opa|e a[ií]|salve)\b",
    ]
    _FAREWELL_PATTERNS = [
        r"\b(tchau|at[eé] mais|at[eé] logo|falou|valeu|at[eé] amanh[aã]|abra[çc]o)\b",
    ]
    _ACKNOWLEDGMENT_PATTERNS = [
        r"\b(obrigad[oa]|valeu|agrade[çc]o|tks|thanks|gratid[aã]o)\b",
    ]
    _INVITATION_PATTERNS = [
        r"\b(vamos|bora|quer ir|topa|partiu|animar?|combina[rm]|almo[çc]ar|jantar)\b",
    ]
    _DEMAND_PATTERNS = [
        r"\b(preciso disso|cad[eê]|ainda n[aã]o|quando vai|urgente|atrasad[oa])\b",
    ]
    _REQUEST_PATTERNS = [
        r"\b(pode me|consegue|faz favor|d[aá] pra|me ajuda|me envia|me passa)\b",
    ]

    # Palavras indicativas de tons
    _URGENT_WORDS = {"urgente", "emergência", "urgentemente", "imediato", "asap"}
    _AFFECTIONATE_WORDS = {"querido", "querida", "amigo", "amiga", "abraço", "beijo", "saudades", "amor"}
    _IRRITATED_WORDS = {"saco", "droga", "raiva", "merda", "palhaçada", "inaceitável", "absurdo"}

    def interpret(self, message: ReceivedMessage) -> MessageInterpretation:
        """Interpreta uma mensagem recebida usando regras léxicas e heurísticas."""
        text = message.content.strip()
        lower_text = text.lower()

        # 1. Identificar Intenção
        intent = self._detect_intent(text, lower_text)

        # 2. Identificar Tons
        tones = self._detect_tones(lower_text)

        # 3. Calcular Urgência (1 a 5)
        urgency = self._calculate_urgency(lower_text, tones)

        # 4. Verificar se requer resposta
        requires_response = self._check_requires_response(intent, text)

        # 5. Detectar sinais contextuais (inferências)
        signals = self._extract_signals(lower_text)

        # 6. Resumo simples
        summary = self._generate_summary(intent, text)

        return MessageInterpretation(
            message=message,
            intent=intent,
            tones=tones,
            urgency_level=urgency,
            topics=[],
            requires_response=requires_response,
            signals=signals,
            summary=summary,
        )

    def _detect_intent(self, text: str, lower_text: str) -> MessageIntent:
        # Pergunta explícita por pontuação ou pronomes interrogativos
        if "?" in text:
            # Se também tiver padrão de convite
            if self._matches_any(self._INVITATION_PATTERNS, lower_text):
                return MessageIntent(
                    category=MessageIntentCategory.INVITATION,
                    description="Convite ou proposta de encontro",
                    confidence=0.85,
                )
            if self._matches_any(self._REQUEST_PATTERNS, lower_text):
                return MessageIntent(
                    category=MessageIntentCategory.REQUEST,
                    description="Solicitação ou pedido de ajuda",
                    confidence=0.85,
                )
            return MessageIntent(
                category=MessageIntentCategory.QUESTION,
                description="Pergunta direta",
                confidence=0.9,
            )

        # Checar outros padrões em ordem de especificidade
        if self._matches_any(self._INVITATION_PATTERNS, lower_text):
            return MessageIntent(
                category=MessageIntentCategory.INVITATION,
                description="Convite ou proposta",
                confidence=0.8,
            )
        if self._matches_any(self._DEMAND_PATTERNS, lower_text):
            return MessageIntent(
                category=MessageIntentCategory.DEMAND,
                description="Cobrança ou exigência de prazo",
                confidence=0.8,
            )
        if self._matches_any(self._REQUEST_PATTERNS, lower_text):
            return MessageIntent(
                category=MessageIntentCategory.REQUEST,
                description="Solicitação ou pedido",
                confidence=0.8,
            )
        if self._matches_any(self._ACKNOWLEDGMENT_PATTERNS, lower_text):
            return MessageIntent(
                category=MessageIntentCategory.ACKNOWLEDGMENT,
                description="Agradecimento ou confirmação",
                confidence=0.85,
            )
        if self._matches_any(self._FAREWELL_PATTERNS, lower_text):
            return MessageIntent(
                category=MessageIntentCategory.FAREWELL,
                description="Despedida",
                confidence=0.85,
            )
        if self._matches_any(self._GREETING_PATTERNS, lower_text):
            return MessageIntent(
                category=MessageIntentCategory.GREETING,
                description="Saudação inicial",
                confidence=0.85,
            )

        return MessageIntent(
            category=MessageIntentCategory.INFORMATIONAL,
            description="Compartilhamento de informação ou declaração",
            confidence=0.6,
        )

    def _detect_tones(self, lower_text: str) -> List[MessageTone]:
        tones: List[MessageTone] = []
        words = set(re.findall(r"\w+", lower_text))

        # Urgência por termos explícitos ou múltiplos pontos de exclamação
        if (words & self._URGENT_WORDS) or lower_text.count("!") >= 2:
            tones.append(MessageTone.URGENT)

        if words & self._AFFECTIONATE_WORDS:
            tones.append(MessageTone.AFFECTIONATE)

        if words & self._IRRITATED_WORDS:
            tones.append(MessageTone.IRRITATED)

        # Formalidade vs Casualidade
        if any(w in words for w in {"prezado", "senhor", "senhora", "atenciosamente", "cordialmente"}):
            tones.append(MessageTone.FORMAL)
        elif any(w in words for w in {"vc", "pq", "tb", "tbm", "blz", "mano", "valeu", "bora"}):
            tones.append(MessageTone.CASUAL)

        if not tones:
            tones.append(MessageTone.NEUTRAL)

        return tones

    def _calculate_urgency(self, lower_text: str, tones: List[MessageTone]) -> int:
        urgency = 1
        if MessageTone.URGENT in tones:
            urgency += 2
        if any(w in lower_text for w in {"urgente", "imediato", "asap"}):
            urgency += 1
        if lower_text.count("!") >= 2:
            urgency += 1
        return min(max(urgency, 1), 5)

    def _check_requires_response(self, intent: MessageIntent, text: str) -> bool:
        if intent.category in {
            MessageIntentCategory.QUESTION,
            MessageIntentCategory.INVITATION,
            MessageIntentCategory.REQUEST,
            MessageIntentCategory.DEMAND,
        }:
            return True
        if intent.category in {MessageIntentCategory.ACKNOWLEDGMENT, MessageIntentCategory.FAREWELL}:
            return False
        return "?" in text

    def _extract_signals(self, lower_text: str) -> List[ContextSignal]:
        signals: List[ContextSignal] = []
        # Detecção de referências temporais (sempre como inferência, per AGENTS.md Seção 6.2)
        time_refs = re.findall(r"\b(amanh[aã]|hoje|ontem|segunda|ter[çc]a|quarta|quinta|sexta|s[aá]bado|domingo)\b", lower_text)
        for ref in set(time_refs):
            signals.append(
                ContextSignal(
                    content=f"Referência temporal: {ref}",
                    signal_type="temporal_reference",
                    is_inference=True,
                    confidence=0.7,
                )
            )
        return signals

    def _generate_summary(self, intent: MessageIntent, text: str) -> str:
        snippet = text if len(text) <= 50 else text[:47] + "..."
        return f"{intent.description}: '{snippet}'"

    @staticmethod
    def _matches_any(patterns: List[str], text: str) -> bool:
        return any(re.search(pat, text, re.IGNORECASE) for pat in patterns)
