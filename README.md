# Esqueleto Python da Atividade 08

Projeto de agendamentos da clínica popular. Grupo desenvolvedor F, cliente G.
Python 3.10 ou posterior, apenas biblioteca padrão, sem instalação de pacotes.

Na pasta que contém `clinica/`, execute:

```powershell
python -m clinica
python -m unittest discover -s tests -v
```

Também acompanha a entrega o executável de demonstração `clinica-demo.pyz`.
Ele pode ser iniciado com `python clinica-demo.pyz`.

## Correspondência arquitetural

- `dominio/`: conceitos e regras de intervalos, dados de referência e agenda planejada.
- `portas/`: IAgendamento, IRepositorioAgendamento e INotificacao.
- `aplicacao/`: ControladorAgenda realiza UC04 e UC05.
- `apresentacao/`: InterfaceAgenda demonstra a fronteira operacional via console.
- `infraestrutura/`: armazenamento e pedidos de notificação em memória.
- `composicao.py`: liga os adaptadores aos contratos e fornece dados fictícios.

Consulta no esboço da Bônus 5 corresponde a Agendamento nesta consolidação.
O serviço de exemplo dura 30 minutos e tem uma janela de quatro horas.
A situação inicial e as situações que permitem reagendamento também são
configuração da demonstração. Esses valores não são regras validadas da clínica.

## O que a demonstração verifica

Reservas do mesmo profissional não podem ter intervalos sobrepostos. A troca
usa uma nova instância imutável e só substitui o registro após as verificações.
Uma versão antiga não pode sobrescrever uma alteração posterior. O bloqueio
RLock preserva a atomicidade apenas dentro deste processo Python.

A notificação aceita pedidos em memória. Não há envio real, processamento
assíncrono em segundo plano nem garantia durável de entrega. Um retorno
aviso_aceito=False sinaliza falha nessa etapa sem apagar uma reserva válida.

## Relação com a implantação proposta no PDF

O diagrama principal de implantação especifica uma evolução web em Python,
com banco persistente e provedor externo. A figura de demonstração local
descreve exatamente o que foi executado neste esqueleto.

O adaptador HTTP, autenticação/autorização, armazenamento PostgreSQL,
restrições transacionais entre processos, auditoria, backup e integração
real de mensagens permanecem pontos de implementação. A geração de um
pacote executável não comprova o atendimento dos RNFs quantitativos.

O repositório demonstrativo contém somente reservas ativas dos cenários
Agendar e Reagendar. Cancelar e gerenciar todo o ciclo de vida não estão
implementados; uma versão completa deverá definir quais situações ocupam
a agenda e preservar o histórico conforme a A04.
