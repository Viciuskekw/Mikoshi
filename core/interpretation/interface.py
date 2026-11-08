"""Interface para interpretação de mensagens recebidas no Mikoshi."""

from abc import ABC, abstractmethod
from core.interpretation.models import MessageInterpretation, ReceivedMessage


class MessageInterpreter(ABC):
    """Interface abstrata mínima para interpretação de mensagens recebidas.

    Qualquer implementação (baseada em regras locais, heurísticas ou modelos
    de linguagem) deve herdar desta classe e implementar o método `interpret`.
    """

    @abstractmethod
    def interpret(self, message: ReceivedMessage) -> MessageInterpretation:
        """Interpreta uma mensagem recebida e retorna a interpretação estruturada.

        Args:
            message: Objeto ReceivedMessage contendo conteúdo e metadados da mensagem.

        Returns:
            MessageInterpretation com intenção, tons, urgência, tópicos e sinais.
        """
        raise NotImplementedError

