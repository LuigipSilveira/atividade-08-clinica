"""Adaptador demonstrativo. A exclusão mútua protege apenas este processo."""
from threading import RLock
from clinica.dominio.modelos import Agendamento, DadosInvalidos, HorarioIndisponivel, AlteracaoConcorrente
from clinica.portas.contratos import IRepositorioAgendamento


class RepositorioAgendamentoMemoria(IRepositorioAgendamento):
    def __init__(self):
        self._reservas: dict[str, Agendamento] = {}
        self._lock = RLock()

    def obter(self, agendamento_id):
        with self._lock:
            try:
                return self._reservas[agendamento_id]
            except KeyError as exc:
                raise DadosInvalidos("Agendamento não localizado.") from exc

    def _verificar(self, novo, ignorar_id=None):
        for atual in self._reservas.values():
            if (atual.id != ignorar_id
                    and atual.profissional_id == novo.profissional_id
                    and atual.intervalo.sobrepoe(novo.intervalo)):
                raise HorarioIndisponivel("Intervalo ocupado por outra reserva.")

    def registrar_se_disponivel(self, novo):
        with self._lock:
            if novo.id in self._reservas:
                raise DadosInvalidos("Identificador já registrado.")
            self._verificar(novo)
            self._reservas[novo.id] = novo

    def substituir_se_disponivel(self, esperado, novo):
        with self._lock:
            atual = self.obter(esperado.id)
            if atual.versao != esperado.versao:
                raise AlteracaoConcorrente("A reserva foi alterada; atualize os dados.")
            if novo.id != atual.id or novo.versao != atual.versao + 1:
                raise DadosInvalidos("A substituição deve preservar a identidade e avançar a versão.")
            self._verificar(novo, ignorar_id=atual.id)
            self._reservas[atual.id] = novo

    def listar(self):
        with self._lock:
            return tuple(self._reservas.values())
