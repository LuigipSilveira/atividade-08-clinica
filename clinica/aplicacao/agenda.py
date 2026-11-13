"""Realização de UC04/UC05: coordenação sem detalhes dos adaptadores."""
from datetime import timedelta
from uuid import uuid4
from clinica.dominio.modelos import Agendamento, CatalogoClinica, AgendaProfissional, Intervalo
from clinica.portas.contratos import IRepositorioAgendamento, INotificacao, ResultadoReserva


class ControladorAgenda:
    def __init__(self, repositorio: IRepositorioAgendamento, notificacao: INotificacao,
                 catalogo: CatalogoClinica, agenda: AgendaProfissional,
                 situacao_inicial: str):
        self.repositorio = repositorio
        self.notificacao = notificacao
        self.catalogo = catalogo
        self.agenda = agenda
        self.situacao_inicial = situacao_inicial

    def _intervalo(self, paciente_id, profissional_id, servico_id, inicio):
        servico = self.catalogo.validar_referencias(paciente_id, profissional_id, servico_id)
        intervalo = Intervalo(inicio, inicio + timedelta(minutes=servico.duracao_minutos))
        self.agenda.validar_horario(profissional_id, servico_id, intervalo)
        return intervalo

    def agendar(self, paciente_id, profissional_id, servico_id, inicio):
        intervalo = self._intervalo(paciente_id, profissional_id, servico_id, inicio)
        novo = Agendamento(str(uuid4()), paciente_id, profissional_id,
                           servico_id, intervalo, self.situacao_inicial)
        # A consulta de opções anterior não substitui a proteção no armazenamento.
        self.repositorio.registrar_se_disponivel(novo)
        return ResultadoReserva(novo, self._solicitar_aviso(novo, "criada"))

    def reagendar(self, agendamento_id, profissional_id, inicio):
        original = self.repositorio.obter(agendamento_id)
        self.agenda.validar_reagendamento(original)
        intervalo = self._intervalo(original.paciente_id, profissional_id,
                                    original.servico_id, inicio)
        proposta = original.reagendado(profissional_id, intervalo)
        # Nenhuma mutação da reserva original acontece antes da troca atômica.
        self.repositorio.substituir_se_disponivel(original, proposta)
        return ResultadoReserva(proposta, self._solicitar_aviso(proposta, "alterada"))

    def _solicitar_aviso(self, agendamento, motivo):
        try:
            self.notificacao.solicitar(agendamento, motivo)
            return True
        except Exception:
            # Reserva já válida: o retorno distingue falha do aviso de falha da reserva.
            # Produção exige observabilidade e mecanismo durável, fora deste esqueleto.
            return False
