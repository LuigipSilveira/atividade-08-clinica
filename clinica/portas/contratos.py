"""Interfaces estáveis do diagrama de componentes da A08."""
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from clinica.dominio.modelos import Agendamento


@dataclass(frozen=True)
class ResultadoReserva:
    agendamento: Agendamento
    aviso_aceito: bool


class IAgendamento(Protocol):
    def agendar(self, paciente_id: str, profissional_id: str,
                servico_id: str, inicio: datetime) -> ResultadoReserva: ...

    def reagendar(self, agendamento_id: str, profissional_id: str,
                  inicio: datetime) -> ResultadoReserva: ...


class IRepositorioAgendamento(Protocol):
    def obter(self, agendamento_id: str) -> Agendamento: ...

    def registrar_se_disponivel(self, novo: Agendamento) -> None:
        """Verificar conflitos e inserir como uma unidade atômica."""
        ...

    def substituir_se_disponivel(self, esperado: Agendamento, novo: Agendamento) -> None:
        """Conferir versão/conflitos e trocar; em falha, preservar o original."""
        ...


class INotificacao(Protocol):
    def solicitar(self, agendamento: Agendamento, motivo: str) -> None:
        """Aceitar um pedido de aviso. Não significa mensagem entregue."""
        ...
