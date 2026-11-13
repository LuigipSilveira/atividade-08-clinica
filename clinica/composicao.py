"""Único ponto que conhece implementações concretas. Dados fictícios de demonstração."""
from datetime import datetime, timedelta, timezone
from clinica.dominio.modelos import (Paciente, ProfissionalSaude, Servico, CatalogoClinica,
                                     AgendaProfissional, Intervalo, HorarioIndisponivel)
from clinica.aplicacao.agenda import ControladorAgenda
from clinica.apresentacao.console import InterfaceAgenda
from clinica.infraestrutura.memoria import RepositorioAgendamentoMemoria
from clinica.infraestrutura.notificacoes import NotificacaoMemoria

INICIO_EXEMPLO = datetime(2026, 11, 6, 9, 0, tzinfo=timezone(timedelta(hours=-3)))


def criar_demo():
    catalogo = CatalogoClinica(
        {"p1": Paciente("p1", "Paciente de exemplo")},
        {"m1": ProfissionalSaude("m1", "Profissional de exemplo")},
        {"s1": Servico("s1", "Serviço de exemplo", 30)},
    )
    # Estes valores permitem executar cenários; não documentam acordo com o cliente.
    agenda = AgendaProfissional(
        {"m1": (Intervalo(INICIO_EXEMPLO, INICIO_EXEMPLO + timedelta(hours=4)),)},
        frozenset({("m1", "s1")}), frozenset({"AGENDADA"}),
    )
    repo, avisos = RepositorioAgendamentoMemoria(), NotificacaoMemoria()
    controlador = ControladorAgenda(repo, avisos, catalogo, agenda, "AGENDADA")
    return InterfaceAgenda(controlador), controlador, repo, avisos


def main():
    tela, _, repo, avisos = criar_demo()
    a = tela.agendar("p1", "m1", "s1", INICIO_EXEMPLO).agendamento
    print("Reserva criada:", a.intervalo.inicio.isoformat())
    try:
        tela.agendar("p1", "m1", "s1", INICIO_EXEMPLO)
    except HorarioIndisponivel:
        print("Conflito rejeitado: nenhuma reserva duplicada.")
    tela.agendar("p1", "m1", "s1", INICIO_EXEMPLO + timedelta(hours=1))
    try:
        tela.reagendar(a.id, "m1", INICIO_EXEMPLO + timedelta(hours=1))
    except HorarioIndisponivel:
        print("Troca rejeitada: reserva original preservada =", repo.obter(a.id) == a)
    nova = tela.reagendar(a.id, "m1", INICIO_EXEMPLO + timedelta(hours=2)).agendamento
    print("Troca concluída:", nova.intervalo.inicio.isoformat(), "versão", nova.versao)
    print("Pedidos de aviso aceitos, sem envio real:", len(avisos.pendentes))


if __name__ == "__main__":
    main()
