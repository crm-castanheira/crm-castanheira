from datetime import date

from flask import Blueprint, jsonify

from models import Cliente, Processo, Prazo, Publicacao, Tarefa

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/resumo')
def resumo():
    hoje         = date.today()
    prazos_todos = Prazo.query.filter_by(status='Pendente').all()
    urgentes     = [p for p in prazos_todos if p.dias_restantes <= 2]
    semana       = [p for p in prazos_todos if 0 <= p.dias_restantes <= 7]

    return jsonify({
        'data':             hoje.strftime('%d/%m/%Y'),
        'processos_ativos': Processo.query.filter_by(status='Ativo').count(),
        'prazos_urgentes':  len(urgentes),
        'prazos_semana':    len(semana),
        'tarefas_abertas':  Tarefa.query.filter(Tarefa.status != 'concluida').count(),
        'pubs_pendentes':   Publicacao.query.filter_by(prazo_gerado=False).count(),
        'clientes':         Cliente.query.count(),
        'urgentes': [
            {
                'proc':  p.processo.numero if p.processo else '—',
                'tipo':  p.tipo,
                'vence': p.data_venc.strftime('%d/%m/%Y'),
                'dias':  p.dias_restantes,
            }
            for p in urgentes
        ],
    })
