"""
Seed — processos e tarefas reais de Castanheira e Reis Advogados Associados.

Como usar:
    python seed.py

Idempotente: verifica número do processo / título da tarefa antes de inserir.
"""
import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from extensions import db
from models import Cliente, Processo, Tarefa


# ── Mapeamento de comarca por sufixo do número CNJ ───────────────────────────
def _comarca(numero: str) -> str:
    if '0514' in numero:
        return 'Divinópolis'
    if '0076' in numero or '0148' in numero:
        return 'Belo Horizonte'
    return 'Divinópolis'


def _tribunal(numero: str) -> str:
    if numero.startswith('001') and '.5.' in numero:
        return 'TRT-3'
    if '.5.' in numero:
        return 'TRT-3'
    return 'TJMG'


def _prazo_dt(dias):
    if not dias:
        return None
    return date.today() + timedelta(days=dias)


# ── Dados reais ───────────────────────────────────────────────────────────────
PROCESSOS_TAREFAS = [
    {
        'processo': {
            'numero':  '1000418-83.2026.8.13.0514',
            'tipo':    'Execução',
            'polo':    'Autor',
            'vara':    '',
            'status':  'Ativo',
        },
        'tarefa': {
            'titulo':     'Planilha de débito + impulsionar execução (SISBAJUD/RENAJUD/INFOJUD) — 1000418-83.2026.8.13.0514',
            'descricao':  'Elaborar e protocolar planilha de débito atualizada + impulsionar execução após mandado negativo (indicar endereço e requerer SISBAJUD, RENAJUD, INFOJUD). Unificar em uma única petição estratégica.',
            'prioridade': 'urgente',
            'prazo_dias': 5,
            'tipo':       'peticao',
        },
    },
    {
        'processo': {
            'numero':  '1000300-10.2026.8.13.0514',
            'tipo':    'Execução',
            'polo':    'Autor',
            'vara':    '',
            'status':  'Ativo',
        },
        'tarefa': {
            'titulo':     'Redistribuir ação no foro competente (São Paulo) — 1000300-10.2026.8.13.0514',
            'descricao':  'Redistribuir ação no foro competente (São Paulo — local da agência bancária). Processo extinto por incompetência territorial.',
            'prioridade': 'urgente',
            'prazo_dias': None,
            'tipo':       'peticao',
        },
    },
    {
        'processo': {
            'numero':  '5003947-76.2025.8.13.0514',
            'tipo':    'Cumprimento de Sentença',
            'polo':    'Autor',
            'vara':    '',
            'status':  'Ativo',
        },
        'tarefa': {
            'titulo':     'RENAJUD + impulsionar execução — 5003947-76.2025.8.13.0514',
            'descricao':  'Verificar existência de veículos no DETRAN e requerer bloqueio via RENAJUD + peticionar impulsionando execução. Evitar extinção do feito.',
            'prioridade': 'urgente',
            'prazo_dias': 10,
            'tipo':       'peticao',
        },
    },
    {
        'processo': {
            'numero':  '0010595-85.2026.5.03.0148',
            'tipo':    'Trabalhista',
            'polo':    'Autor',
            'vara':    '',
            'status':  'Ativo',
        },
        'tarefa': {
            'titulo':     'Verificar decisão TRT e acompanhar acordo — 0010595-85.2026.5.03.0148',
            'descricao':  'Verificar decisão no TRT e acompanhar cumprimento de acordo em processo vinculado. Processo sobrestado.',
            'prioridade': 'normal',
            'prazo_dias': None,
            'tipo':       'pesquisa',
        },
    },
    {
        'processo': {
            'numero':  '1000782-55.2026.8.13.0514',
            'tipo':    'Reclamação Pré-Processual',
            'polo':    'Autor',
            'vara':    '',
            'status':  'Ativo',
        },
        'tarefa': {
            'titulo':     'Verificar audiência e comunicar cliente — 1000782-55.2026.8.13.0514',
            'descricao':  'Verificar data da audiência e enviar comunicação ao cliente.',
            'prioridade': 'normal',
            'prazo_dias': None,
            'tipo':       'pesquisa',
        },
    },
    {
        'processo': {
            'numero':  '1000863-04.2026.8.13.0514',
            'tipo':    'Reclamação Pré-Processual',
            'polo':    'Autor',
            'vara':    '',
            'status':  'Ativo',
        },
        'tarefa': {
            'titulo':     'Verificar audiência e comunicar cliente — 1000863-04.2026.8.13.0514',
            'descricao':  'Verificar data da audiência e enviar comunicação ao cliente.',
            'prioridade': 'normal',
            'prazo_dias': None,
            'tipo':       'pesquisa',
        },
    },
    {
        'processo': {
            'numero':  '1000862-19.2026.8.13.0514',
            'tipo':    'Reclamação Pré-Processual',
            'polo':    'Autor',
            'vara':    '',
            'status':  'Ativo',
        },
        'tarefa': {
            'titulo':     'Verificar audiência e comunicar cliente — 1000862-19.2026.8.13.0514',
            'descricao':  'Verificar data da audiência e enviar comunicação ao cliente.',
            'prioridade': 'normal',
            'prazo_dias': None,
            'tipo':       'pesquisa',
        },
    },
    {
        'processo': {
            'numero':  '1000861-34.2026.8.13.0514',
            'tipo':    'Reclamação Pré-Processual',
            'polo':    'Autor',
            'vara':    '',
            'status':  'Ativo',
        },
        'tarefa': {
            'titulo':     'Verificar audiência e comunicar cliente — 1000861-34.2026.8.13.0514',
            'descricao':  'Verificar data da audiência e enviar comunicação ao cliente.',
            'prioridade': 'normal',
            'prazo_dias': None,
            'tipo':       'pesquisa',
        },
    },
    {
        'processo': {
            'numero':  '1000849-20.2026.8.13.0514',
            'tipo':    'Reclamação Pré-Processual',
            'polo':    'Autor',
            'vara':    '',
            'status':  'Ativo',
        },
        'tarefa': {
            'titulo':     'Verificar audiência e comunicar cliente — 1000849-20.2026.8.13.0514',
            'descricao':  'Verificar data da audiência e enviar comunicação ao cliente.',
            'prioridade': 'normal',
            'prazo_dias': None,
            'tipo':       'pesquisa',
        },
    },
    {
        'processo': {
            'numero':  '5001911-95.2024.8.13.0514',
            'tipo':    'Busca e Apreensão',
            'polo':    'Réu',
            'vara':    '',
            'status':  'Ativo',
        },
        'tarefa': {
            'titulo':     'Protocolar pedido de justiça gratuita para a ré — 5001911-95.2024.8.13.0514',
            'descricao':  'Protocolar pedido de justiça gratuita para a ré. Evitar execução de custas / inscrição em dívida ativa.',
            'prioridade': 'urgente',
            'prazo_dias': 7,
            'tipo':       'peticao',
        },
    },
    {
        'processo': {
            'numero':  '5003945-77.2023.8.13.0514',
            'tipo':    'Procedimento Comum',
            'polo':    'Autor',
            'vara':    '',
            'status':  'Ativo',
        },
        'tarefa': {
            'titulo':     'Especificação de provas ou julgamento antecipado — 5003945-77.2023.8.13.0514',
            'descricao':  'Analisar estratégia e protocolar especificação de provas ou requerer julgamento antecipado. Evitar indeferimento por pedido genérico.',
            'prioridade': 'urgente',
            'prazo_dias': 15,
            'tipo':       'peticao',
        },
    },
    {
        'processo': {
            'numero':  '5002272-15.2024.8.13.0514',
            'tipo':    'Procedimento Comum',
            'polo':    'Autor',
            'vara':    '',
            'status':  'Ativo',
        },
        'tarefa': {
            'titulo':     'Analisar acórdão + justiça gratuita — 5002272-15.2024.8.13.0514',
            'descricao':  'Analisar acórdão e protocolar manifestação requerendo justiça gratuita.',
            'prioridade': 'urgente',
            'prazo_dias': 5,
            'tipo':       'peticao',
        },
    },
    {
        'processo': {
            'numero':  '0010093-71.2026.5.03.0076',
            'tipo':    'Trabalhista',
            'polo':    'Autor',
            'vara':    '',
            'status':  'Ativo',
        },
        'tarefa': {
            'titulo':     'Orientar testemunhas para audiência — 0010093-71.2026.5.03.0076',
            'descricao':  'Verificar despacho e orientar testemunhas para comparecimento espontâneo em audiência.',
            'prioridade': 'normal',
            'prazo_dias': None,
            'tipo':       'pesquisa',
        },
    },
    {
        'processo': {
            'numero':  '1518021-05.2026.8.13.0000',
            'tipo':    'Agravo',
            'polo':    'Autor',
            'vara':    '',
            'status':  'Ativo',
        },
        'tarefa': {
            'titulo':     'Avaliar recurso após negativa de provimento (STJ/embargos) — 1518021-05.2026.8.13.0000',
            'descricao':  'Analisar decisão que negou provimento e avaliar recurso (STJ ou embargos). Definir estratégia recursal.',
            'prioridade': 'urgente',
            'prazo_dias': 15,
            'tipo':       'recurso',
        },
    },
    {
        'processo': {
            'numero':  '5005079-42.2023.8.13.0514',
            'tipo':    'Procedimento Cível',
            'polo':    'Autor',
            'vara':    '',
            'status':  'Ativo',
        },
        'tarefa': {
            'titulo':     'Analisar sentença e verificar recurso — 5005079-42.2023.8.13.0514',
            'descricao':  'Analisar sentença e verificar necessidade de recurso.',
            'prioridade': 'urgente',
            'prazo_dias': 15,
            'tipo':       'recurso',
        },
    },
    {
        'processo': {
            'numero':  '1.0000.26.126799-1/001',
            'tipo':    'Agravo de Instrumento',
            'polo':    'Autor',
            'vara':    '',
            'status':  'Ativo',
        },
        'tarefa': {
            'titulo':     '[CRÍTICO] Comprovação de hipossuficiência — 1.0000.26.126799-1/001',
            'descricao':  'Verificar andamento e protocolar comprovação de hipossuficiência com documentos completos. Risco de indeferimento da justiça gratuita.',
            'prioridade': 'urgente',
            'prazo_dias': 5,
            'tipo':       'peticao',
        },
    },
]
# ─────────────────────────────────────────────────────────────────────────────


def run():
    app = create_app()
    with app.app_context():
        processos_inseridos = 0
        processos_pulados   = 0
        tarefas_inseridas   = 0
        tarefas_puladas     = 0

        for item in PROCESSOS_TAREFAS:
            pd = item['processo']
            td = item['tarefa']

            # ── Processo ─────────────────────────────────────────────────────
            proc = Processo.query.filter_by(numero=pd['numero']).first()
            if not proc:
                proc = Processo(
                    numero   = pd['numero'],
                    tipo     = pd['tipo'],
                    polo     = pd['polo'],
                    vara     = pd.get('vara', ''),
                    comarca  = _comarca(pd['numero']),
                    status   = pd.get('status', 'Ativo'),
                )
                db.session.add(proc)
                db.session.flush()
                processos_inseridos += 1
                print(f"  [+] Processo: {pd['numero']}")
            else:
                processos_pulados += 1
                print(f"  [skip] Processo já existe: {pd['numero']}")

            # ── Tarefa vinculada ─────────────────────────────────────────────
            existe_tarefa = Tarefa.query.filter_by(
                titulo      = td['titulo'],
                processo_id = proc.id,
            ).first()

            if not existe_tarefa:
                t = Tarefa(
                    titulo      = td['titulo'],
                    descricao   = td['descricao'],
                    tipo        = td.get('tipo', 'peticao'),
                    origem      = 'pessoal',
                    prioridade  = td['prioridade'],
                    prazo_data  = _prazo_dt(td['prazo_dias']),
                    processo_id = proc.id,
                    responsavel = 'Jardel',
                    criado_por  = 'Jardel',
                )
                db.session.add(t)
                tarefas_inseridas += 1
                print(f"       → Tarefa: {td['titulo'][:70]}")
            else:
                tarefas_puladas += 1
                print(f"       → [skip] Tarefa já existe")

        db.session.commit()
        print(f"\nConcluído:")
        print(f"  Processos: {processos_inseridos} inseridos, {processos_pulados} pulados")
        print(f"  Tarefas:   {tarefas_inseridas} inseridas, {tarefas_puladas} puladas")


if __name__ == '__main__':
    run()
