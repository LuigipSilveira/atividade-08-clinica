"""Conceitos da Bônus 2 e invariantes de reserva da A04; sem infraestrutura."""
from dataclasses import dataclass, replace
from datetime import datetime


class ErroAgenda(Exception):
    pass


class DadosInvalidos(ErroAgenda):
    pass


class HorarioIndisponivel(ErroAgenda):
    pass


class AlteracaoConcorrente(ErroAgenda):
    pass


class OperacaoImpedida(ErroAgenda):
    pass


@dataclass(frozen=True)
class Intervalo:
    inicio: datetime
    fim: datetime

    def __post_init__(self):
        if self.inicio.utcoffset() is None or self.fim.utcoffset() is None:
            raise DadosInvalidos("Informe data e hora com fuso horário.")
        if self.inicio >= self.fim:
            raise DadosInvalidos("O fim deve ser posterior ao início.")

    def sobrepoe(self, outro: "Intervalo") -> bool:
        # Intervalos adjacentes não disputam tempo: [início, fim).
        return self.inicio < outro.fim and outro.inicio < self.fim

    def contem(self, outro: "Intervalo") -> bool:
        return self.inicio <= outro.inicio and outro.fim <= self.fim


@dataclass(frozen=True)
class Paciente:
    id: str
    nome: str


@dataclass(frozen=True)
class ProfissionalSaude:
    id: str
    nome: str


@dataclass(frozen=True)
class Servico:
    id: str
    nome: str
    duracao_minutos: int

    def __post_init__(self):
        if self.duracao_minutos <= 0:
            raise DadosInvalidos("A duração do serviço deve ser positiva.")


@dataclass(frozen=True)
class Agendamento:
    id: str
    paciente_id: str
    profissional_id: str
    servico_id: str
    intervalo: Intervalo
    situacao: str
    versao: int = 1

    def reagendado(self, profissional_id: str, intervalo: Intervalo) -> "Agendamento":
        # Constrói uma proposta imutável. A reserva armazenada continua intacta.
        return replace(self, profissional_id=profissional_id,
                       intervalo=intervalo, versao=self.versao + 1)


@dataclass
class CatalogoClinica:
    """Dados de referência carregados na composição; manutenção fora deste recorte."""
    pacientes: dict[str, Paciente]
    profissionais: dict[str, ProfissionalSaude]
    servicos: dict[str, Servico]

    def validar_referencias(self, paciente_id, profissional_id, servico_id) -> Servico:
        if paciente_id not in self.pacientes:
            raise DadosInvalidos("Paciente não localizado.")
        if profissional_id not in self.profissionais:
            raise DadosInvalidos("Profissional não localizado.")
        if servico_id not in self.servicos:
            raise DadosInvalidos("Serviço não localizado.")
        return self.servicos[servico_id]


@dataclass(frozen=True)
class AgendaProfissional:
    """Configuração injetada. Valores do exemplo não são políticas do cliente."""
    periodos: dict[str, tuple[Intervalo, ...]]
    habilitacoes: frozenset[tuple[str, str]]
    situacoes_reagendaveis: frozenset[str]

    def validar_horario(self, profissional_id, servico_id, intervalo):
        if (profissional_id, servico_id) not in self.habilitacoes:
            raise OperacaoImpedida("Profissional não habilitado para o serviço.")
        if not any(p.contem(intervalo) for p in self.periodos.get(profissional_id, ())):
            raise HorarioIndisponivel("Intervalo fora da disponibilidade planejada.")

    def validar_reagendamento(self, agendamento):
        if agendamento.situacao not in self.situacoes_reagendaveis:
            raise OperacaoImpedida("Situação não permite reagendamento nesta configuração.")
