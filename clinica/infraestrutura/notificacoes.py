"""Simulação de aceitação de pedidos; não envia mensagens e não é durável."""
from dataclasses import dataclass
from threading import Lock
from clinica.portas.contratos import INotificacao


@dataclass(frozen=True)
class PedidoAviso:
    agendamento_id: str
    versao: int
    motivo: str


class NotificacaoMemoria(INotificacao):
    def __init__(self):
        self._pedidos = []
        self._lock = Lock()

    def solicitar(self, agendamento, motivo):
        with self._lock:
            self._pedidos.append(PedidoAviso(agendamento.id, agendamento.versao, motivo))

    @property
    def pendentes(self):
        with self._lock:
            return tuple(self._pedidos)
