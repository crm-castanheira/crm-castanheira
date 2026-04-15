from datetime import datetime, date

from flask import Blueprint, render_template, request, redirect, url_for, jsonify

from extensions import db
from models import Prazo, Processo

bp = Blueprint('prazos', __name__, url_prefix='/prazos')


@bp.route('/')
def prazos():
    todos = Prazo.query.filter_by(status='Pendente').all()
    todos = sorted(todos, key=lambda p: p.data_venc)
    cumpridos = (
        Prazo.query
        .filter_by(status='Cumprido')
        .order_by(Prazo.data_venc.desc())
        .limit(10).all()
    )
    return render_template('prazos.html', prazos=todos, cumpridos=cumpridos)


@bp.route('/novo', methods=['GET', 'POST'])
def novo_prazo():
    processos = Processo.query.filter_by(status='Ativo').all()
    if request.method == 'POST':
        venc       = datetime.strptime(request.form['data_venc'], '%Y-%m-%d').date()
        inicio_str = request.form.get('data_inicio')
        inicio     = datetime.strptime(inicio_str, '%Y-%m-%d').date() if inicio_str else date.today()
        pr = Prazo(
            tipo        = request.form['tipo'],
            descricao   = request.form.get('descricao'),
            data_inicio = inicio,
            data_venc   = venc,
            dias        = request.form.get('dias', 15),
            contagem    = request.form.get('contagem', 'Corridos'),
            processo_id = request.form.get('processo_id') or None,
        )
        db.session.add(pr)
        db.session.commit()
        return redirect(url_for('prazos.prazos'))
    return render_template('form_prazo.html', processos=processos)


@bp.route('/<int:id>/cumprir', methods=['POST'])
def cumprir_prazo(id):
    p = Prazo.query.get_or_404(id)
    p.status = 'Cumprido'
    db.session.commit()
    return jsonify({'ok': True})
