"""Fronteira demonstrativa substituível por um adaptador HTTP futuro."""
from clinica.portas.contratos import IAgendamento


class InterfaceAgenda:
    def __init__(self, agenda: IAgendamento):
        self.agenda = agenda

    def agendar(self, paciente_id, profissional_id, servico_id, inicio):
        return self.agenda.agendar(paciente_id, profissional_id, servico_id, inicio)

    def reagendar(self, agendamento_id, profissional_id, inicio):
        return self.agenda.reagendar(agendamento_id, profissional_id, inicio)
