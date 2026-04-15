from datetime import date, datetime

from flask import Blueprint, render_template, request, redirect, url_for, jsonify

from extensions import db
from models import Processo, Cliente
from models.lancamento import Lancamento

bp = Blueprint('financeiro', __name__, url_prefix='/financeiro')


@bp.route('/')
def financeiro():
    tipo_f   = request.args.get('tipo', '')
    status_f = request.args.get('status', '')

    q = Lancamento.query
    if tipo_f:
        q = q.filter_by(tipo=tipo_f)
    if status_f:
        q = q.filter_by(status=status_f)
    lancamentos = q.order_by(Lancamento.data_venc.asc()).all()

    # métricas
    todos_pendentes = Lancamento.query.filter_by(status='pendente').all()
    a_receber = sum(l.valor for l in todos_pendentes if l.tipo == 'receber')
    a_pagar   = sum(l.valor for l in todos_pendentes if l.tipo == 'pagar')
    vencidos  = [l for l in todos_pendentes if l.atrasado]

    processos = Processo.query.filter_by(status='Ativo').order_by(Processo.numero).all()
    clientes  = Cliente.query.order_by(Cliente.nome).all()

    return render_template('financeiro.html',
        lancamentos=lancamentos,
        a_receber=a_receber,
        a_pagar=a_pagar,
        saldo=a_receber - a_pagar,
        vencidos=len(vencidos),
        processos=processos,
        clientes=clientes,
        tipo_f=tipo_f,
        status_f=status_f,
        today=date.today().isoformat(),
    )


@bp.route('/novo', methods=['POST'])
def novo():
    venc_str = request.form.get('data_venc', '')
    try:
        data_venc = date.fromisoformat(venc_str)
    except ValueError:
        data_venc = date.today()

    l = Lancamento(
        tipo        = request.form.get('tipo', 'receber'),
        descricao   = request.form.get('descricao', '').strip(),
        valor       = float(request.form.get('valor', 0) or 0),
        data_venc   = data_venc,
        categoria   = request.form.get('categoria', ''),
        processo_id = request.form.get('processo_id') or None,
        cliente_id  = request.form.get('cliente_id') or None,
    )
    db.session.add(l)
    db.session.commit()
    return redirect(url_for('financeiro.financeiro'))


@bp.route('/<int:id>/pagar', methods=['POST'])
def pagar(id):
    l = Lancamento.query.get_or_404(id)
    l.status         = 'pago'
    l.data_pagamento = date.today()
    db.session.commit()
    return jsonify({'ok': True})


@bp.route('/<int:id>/cancelar', methods=['POST'])
def cancelar(id):
    l = Lancamento.query.get_or_404(id)
    l.status = 'cancelado'
    db.session.commit()
    return jsonify({'ok': True})


@bp.route('/<int:id>/excluir', methods=['POST'])
def excluir(id):
    l = Lancamento.query.get_or_404(id)
    db.session.delete(l)
    db.session.commit()
    return redirect(url_for('financeiro.financeiro'))
