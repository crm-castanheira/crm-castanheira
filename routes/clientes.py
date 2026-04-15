from flask import Blueprint, render_template, request, redirect, url_for

from extensions import db
from models import Cliente

bp = Blueprint('clientes', __name__, url_prefix='/clientes')


@bp.route('/')
def clientes():
    q     = request.args.get('q', '')
    query = Cliente.query
    if q:
        query = query.filter(Cliente.nome.contains(q) | Cliente.cpf.contains(q))
    items = query.order_by(Cliente.nome).all()
    return render_template('clientes.html', clientes=items, q=q)


@bp.route('/novo', methods=['GET', 'POST'])
def novo_cliente():
    if request.method == 'POST':
        c = Cliente(
            nome     = request.form['nome'],
            cpf      = request.form.get('cpf'),
            telefone = request.form.get('telefone'),
            email    = request.form.get('email'),
            endereco = request.form.get('endereco'),
            obs      = request.form.get('obs'),
        )
        db.session.add(c)
        db.session.commit()
        return redirect(url_for('clientes.clientes'))
    return render_template('form_cliente.html', cliente=None)
