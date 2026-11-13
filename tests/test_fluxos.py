"""Verifica garantias observáveis da A04, além da estrutura de pacotes."""
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from dataclasses import replace
from threading import Barrier
from clinica.composicao import criar_demo, INICIO_EXEMPLO
from clinica.dominio.modelos import (HorarioIndisponivel, AlteracaoConcorrente,
                                     OperacaoImpedida, DadosInvalidos, Intervalo)


class FluxosDeAgenda(unittest.TestCase):
    def setUp(self):
        self.tela, self.ctrl, self.repo, self.avisos = criar_demo()

    def agendar(self, minutos=0):
        return self.tela.agendar("p1", "m1", "s1", INICIO_EXEMPLO + timedelta(minutes=minutos)).agendamento

    def test_sobreposicao_rejeitada_mas_intervalo_adjacente_permitido(self):
        self.agendar()
        with self.assertRaises(HorarioIndisponivel):
            self.agendar(15)
        self.agendar(30)
        self.assertEqual(2, len(self.repo.listar()))

    def test_duas_solicitacoes_concorrentes_nao_duplicam_reserva(self):
        barreira = Barrier(2)
        def tentar(_):
            barreira.wait(timeout=3)
            try:
                self.agendar()
                return True
            except HorarioIndisponivel:
                return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            resultados = list(pool.map(tentar, range(2)))
        self.assertEqual([False, True], sorted(resultados))
        self.assertEqual(1, len(self.repo.listar()))

    def test_reagendamento_em_conflito_preserva_original(self):
        a = self.agendar()
        self.agendar(60)
        with self.assertRaises(HorarioIndisponivel):
            self.tela.reagendar(a.id, "m1", INICIO_EXEMPLO + timedelta(minutes=60))
        self.assertEqual(a, self.repo.obter(a.id))
        self.assertEqual(2, len(self.avisos.pendentes))

    def test_versao_antiga_nao_sobrescreve_nova_reserva(self):
        a = self.agendar()
        atual = self.tela.reagendar(a.id, "m1", INICIO_EXEMPLO + timedelta(hours=1)).agendamento
        tentativa = a.reagendado("m1", Intervalo(INICIO_EXEMPLO, INICIO_EXEMPLO + timedelta(minutes=30)))
        with self.assertRaises(AlteracaoConcorrente):
            self.repo.substituir_se_disponivel(a, tentativa)
        self.assertEqual(atual, self.repo.obter(a.id))

    def test_falha_do_aviso_nao_transforma_reserva_valida_em_erro(self):
        class AvisoIndisponivel:
            def solicitar(self, agendamento, motivo):
                raise OSError("simulação de canal indisponível")
        self.ctrl.notificacao = AvisoIndisponivel()
        resultado = self.tela.agendar("p1", "m1", "s1", INICIO_EXEMPLO)
        self.assertFalse(resultado.aviso_aceito)
        self.assertEqual(resultado.agendamento, self.repo.obter(resultado.agendamento.id))

    def test_politica_injetada_pode_impedir_troca_sem_alterar_original(self):
        a = self.agendar()
        self.ctrl.agenda = replace(self.ctrl.agenda, situacoes_reagendaveis=frozenset())
        with self.assertRaises(OperacaoImpedida):
            self.tela.reagendar(a.id, "m1", INICIO_EXEMPLO + timedelta(hours=1))
        self.assertEqual(a, self.repo.obter(a.id))

    def test_dados_invalidos_e_horario_fora_da_agenda_nao_sao_gravados(self):
        with self.assertRaises(DadosInvalidos):
            self.tela.agendar("inexistente", "m1", "s1", INICIO_EXEMPLO)
        with self.assertRaises(HorarioIndisponivel):
            self.agendar(240)
        self.assertEqual((), self.repo.listar())


if __name__ == "__main__":
    unittest.main()
