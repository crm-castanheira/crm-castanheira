from datetime import date

from flask import Blueprint, render_template

from models import Cliente, Processo, Prazo, Publicacao, Tarefa
from models.lancamento import Lancamento

bp = Blueprint('dashboard', __name__)


@bp.route('/')
def dashboard():
    hoje = date.today()
    processos_ativos = Processo.query.filter_by(status='Ativo').count()
    clientes_total   = Cliente.query.count()

    prazos_todos    = Prazo.query.filter_by(status='Pendente').all()
    prazos_urgentes = [p for p in prazos_todos if p.urgencia in ('urgente', 'vencido')]
    prazos_semana   = [p for p in prazos_todos if 0 <= p.dias_restantes <= 7]

    pubs_nao_tratadas = Publicacao.query.filter_by(status='pendente').count()

    tarefas_abertas = Tarefa.query.filter(
        Tarefa.status != 'concluida',
        Tarefa.tipo   != 'publicacao',
    ).count()

    # Financeiro
    pendentes       = Lancamento.query.filter_by(status='pendente').all()
    fin_vencidos    = [l for l in pendentes if l.atrasado]
    fin_a_receber   = sum(l.valor for l in pendentes if l.tipo == 'receber')
    fin_a_pagar     = sum(l.valor for l in pendentes if l.tipo == 'pagar')

    proximos_prazos = sorted(prazos_todos, key=lambda p: p.data_venc)[:6]
    ultimas_tarefas = (
        Tarefa.query
        .filter(Tarefa.status != 'concluida', Tarefa.tipo != 'publicacao')
        .order_by(Tarefa.criado_em.desc())
        .limit(5).all()
    )
    ultimas_pubs = Publicacao.query.order_by(Publicacao.criado_em.desc()).limit(4).all()

    return render_template('dashboard.html',
        hoje             = hoje,
        processos_ativos = processos_ativos,
        clientes_total   = clientes_total,
        prazos_urgentes  = len(prazos_urgentes),
        prazos_semana    = len(prazos_semana),
        pubs_nao_tratadas= pubs_nao_tratadas,
        tarefas_abertas  = tarefas_abertas,
        fin_vencidos     = len(fin_vencidos),
        fin_a_receber    = fin_a_receber,
        fin_a_pagar      = fin_a_pagar,
        proximos_prazos  = proximos_prazos,
        ultimas_tarefas  = ultimas_tarefas,
        ultimas_pubs     = ultimas_pubs,
    )
