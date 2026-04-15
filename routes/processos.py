from datetime import date

from flask import Blueprint, render_template, request, redirect, url_for

from extensions import db
from models import Cliente, Processo

bp = Blueprint('processos', __name__, url_prefix='/processos')


@bp.route('/')
def processos():
    q      = request.args.get('q', '')
    status = request.args.get('status', '')
    query  = Processo.query
    if q:
        query = query.filter(Processo.numero.contains(q) | Processo.tipo.contains(q))
    if status:
        query = query.filter_by(status=status)
    items = query.order_by(Processo.criado_em.desc()).all()
    return render_template('processos.html', processos=items, q=q, status=status)


@bp.route('/novo', methods=['GET', 'POST'])
def novo_processo():
    clientes = Cliente.query.order_by(Cliente.nome).all()
    if request.method == 'POST':
        p = Processo(
            numero     = request.form.get('numero'),
            tipo       = request.form.get('tipo'),
            polo       = request.form.get('polo', 'Autor'),
            vara       = request.form.get('vara'),
            comarca    = request.form.get('comarca', 'Divinópolis'),
            obs        = request.form.get('obs'),
            cliente_id = request.form.get('cliente_id') or None,
        )
        db.session.add(p)
        db.session.commit()
        return redirect(url_for('processos.processos'))
    return render_template('form_processo.html', clientes=clientes, processo=None)


@bp.route('/<int:id>')
def ver_processo(id):
    p = Processo.query.get_or_404(id)
    return render_template('ver_processo.html', p=p, today=date.today().isoformat())
