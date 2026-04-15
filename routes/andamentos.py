from datetime import date

from flask import Blueprint, redirect, request, url_for

from extensions import db
from models import Processo
from models.andamento import Andamento, classificar_importante

bp = Blueprint('andamentos', __name__)


@bp.route('/processos/<int:processo_id>/andamentos', methods=['POST'])
def criar(processo_id):
    Processo.query.get_or_404(processo_id)
    descricao = request.form.get('descricao', '').strip()
    data_str  = request.form.get('data', '')
    if descricao:
        try:
            data_and = date.fromisoformat(data_str) if data_str else date.today()
        except ValueError:
            data_and = date.today()
        importante = classificar_importante(descricao)
        and_ = Andamento(
            processo_id=processo_id,
            data=data_and,
            descricao=descricao,
            importante=importante,
            origem='manual',
        )
        db.session.add(and_)
        db.session.commit()
    return redirect(url_for('processos.ver_processo', id=processo_id) + '#andamentos')


@bp.route('/andamentos/<int:id>/excluir', methods=['POST'])
def excluir(id):
    and_ = Andamento.query.get_or_404(id)
    processo_id = and_.processo_id
    db.session.delete(and_)
    db.session.commit()
    return redirect(url_for('processos.ver_processo', id=processo_id) + '#andamentos')


@bp.route('/andamentos/<int:id>/importante', methods=['POST'])
def toggle_importante(id):
    and_ = Andamento.query.get_or_404(id)
    and_.importante = not and_.importante
    db.session.commit()
    return redirect(url_for('processos.ver_processo', id=and_.processo_id) + '#andamentos')
