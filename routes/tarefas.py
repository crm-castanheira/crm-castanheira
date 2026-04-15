from datetime import datetime

from flask import Blueprint, render_template, request, jsonify

from extensions import db
from models import Tarefa, Processo, Prazo
from services.ia_service import gerar_sugestao

bp = Blueprint('tarefas', __name__, url_prefix='/tarefas')


@bp.route('/')
def tarefas():
    abertas = (
        Tarefa.query
        .filter(Tarefa.status.notin_(['concluida', 'cancelada']))
        .order_by(Tarefa.criado_em.desc()).all()
    )
    concluidas = (
        Tarefa.query
        .filter_by(status='concluida')
        .order_by(Tarefa.concluida_em.desc())
        .limit(20).all()
    )
    canceladas = (
        Tarefa.query
        .filter_by(status='cancelada')
        .order_by(Tarefa.criado_em.desc())
        .limit(10).all()
    )
    processos = Processo.query.filter_by(status='Ativo').all()
    return render_template('tarefas.html',
        abertas=abertas, concluidas=concluidas,
        canceladas=canceladas, processos=processos)


@bp.route('/nova', methods=['POST'])
def nova_tarefa():
    prazo_str    = request.form.get('prazo_data')
    prazo_dt     = datetime.strptime(prazo_str, '%Y-%m-%d').date() if prazo_str else None
    responsavel  = request.form.get('responsavel', 'Jardel')
    t = Tarefa(
        titulo       = request.form['titulo'],
        tipo         = request.form.get('tipo', 'peticao'),
        origem       = request.form.get('origem', 'pessoal'),
        descricao    = request.form.get('descricao'),
        prioridade   = request.form.get('prioridade', 'normal'),
        prazo_data   = prazo_dt,
        processo_id  = request.form.get('processo_id') or None,
        responsavel  = responsavel,
        criado_por   = responsavel,
    )
    db.session.add(t)
    db.session.commit()
    return jsonify({'ok': True, 'id': t.id})


@bp.route('/<int:id>/concluir', methods=['POST'])
def concluir_tarefa(id):
    t = Tarefa.query.get_or_404(id)
    t.status        = 'concluida'
    t.concluida_em  = datetime.utcnow()
    t.concluida_por = request.form.get('concluida_por', t.responsavel or 'Jardel')

    # Auto-cumprimento: se a tarefa veio de uma publicação, fecha o prazo vinculado
    prazo_fechado = False
    if t.prazo_id:
        pr = Prazo.query.get(t.prazo_id)
        if pr and pr.status == 'Pendente':
            pr.status    = 'Cumprido'
            prazo_fechado = True

    db.session.commit()
    return jsonify({'ok': True, 'prazo_fechado': prazo_fechado})


@bp.route('/<int:id>/cancelar', methods=['POST'])
def cancelar_tarefa(id):
    t = Tarefa.query.get_or_404(id)
    t.status = 'cancelada'
    db.session.commit()
    return jsonify({'ok': True})


@bp.route('/<int:id>/ia', methods=['POST'])
def tarefa_ia(id):
    try:
        sugestao = gerar_sugestao(id)
        return jsonify({'ok': True, 'sugestao': sugestao})
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)})
