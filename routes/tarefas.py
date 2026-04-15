from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, session

from extensions import db
from models import Tarefa, Processo, Prazo
from models.comentario import Comentario
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


@bp.route('/<int:id>/comentar', methods=['POST'])
def comentar_tarefa(id):
    t = Tarefa.query.get_or_404(id)
    data = request.get_json(silent=True) or {}
    texto = (data.get('texto') or '').strip()
    if not texto:
        return jsonify({'ok': False, 'erro': 'Texto vazio'})

    prazo_str = data.get('prazo_data', '')
    prazo_dt  = None
    if prazo_str:
        try:
            prazo_dt = datetime.strptime(prazo_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    autor = session.get('nome', 'Jardel')
    c = Comentario(
        tarefa_id   = t.id,
        texto       = texto,
        tipo        = 'comentario',
        responsavel = data.get('responsavel', 'Jardel'),
        prazo_data  = prazo_dt,
        autor       = autor,
    )
    db.session.add(c)
    db.session.commit()

    return jsonify({
        'ok':          True,
        'id':          c.id,
        'texto':       c.texto,
        'autor':       c.autor,
        'responsavel': c.responsavel,
        'criado_em':   c.criado_em.strftime('%d/%m/%Y %H:%M'),
        'prazo_data':  c.prazo_data.strftime('%d/%m/%Y') if c.prazo_data else None,
        'tipo':        'comentario',
    })


@bp.route('/<int:id>/subtarefa', methods=['POST'])
def criar_subtarefa(id):
    t = Tarefa.query.get_or_404(id)
    data = request.get_json(silent=True) or {}
    titulo = (data.get('titulo') or '').strip()
    if not titulo:
        return jsonify({'ok': False, 'erro': 'Título vazio'})

    prazo_str = data.get('prazo_data', '')
    prazo_dt  = None
    if prazo_str:
        try:
            prazo_dt = datetime.strptime(prazo_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    autor = session.get('nome', 'Jardel')
    sub = Tarefa(
        titulo        = titulo,
        tipo          = t.tipo,
        origem        = 'pessoal',
        prioridade    = 'normal',
        prazo_data    = prazo_dt,
        processo_id   = t.processo_id,
        publicacao_id = t.publicacao_id,
        responsavel   = data.get('responsavel', 'Jardel'),
        criado_por    = autor,
        pai_id        = t.id,
    )
    db.session.add(sub)

    # Registra também como comentário para aparecer no card pai
    c = Comentario(
        tarefa_id   = t.id,
        texto       = titulo,
        tipo        = 'subtarefa',
        responsavel = data.get('responsavel', 'Jardel'),
        prazo_data  = prazo_dt,
        autor       = autor,
    )
    db.session.add(c)
    db.session.commit()

    return jsonify({
        'ok':           True,
        'id':           c.id,
        'subtarefa_id': sub.id,
        'texto':        c.texto,
        'autor':        c.autor,
        'responsavel':  c.responsavel,
        'criado_em':    c.criado_em.strftime('%d/%m/%Y %H:%M'),
        'prazo_data':   c.prazo_data.strftime('%d/%m/%Y') if c.prazo_data else None,
        'tipo':         'subtarefa',
    })
