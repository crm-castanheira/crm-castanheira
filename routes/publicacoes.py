from datetime import datetime, date

from flask import Blueprint, render_template, request, jsonify

from extensions import db
from models import Publicacao, Processo, Prazo, Tarefa
from services.pje_importer import importar_periodo
from services.publicacao_service import (
    criar_tarefa_de_publicacao,
    detectar_efeito_intimatorio,
)
from services.dias_uteis import adicionar_dias_uteis

bp = Blueprint('publicacoes', __name__, url_prefix='/publicacoes')


@bp.route('/')
def publicacoes():
    hoje  = date.today()
    items = Publicacao.query.order_by(Publicacao.data_pub.desc()).all()
    processos = Processo.query.filter_by(status='Ativo').all()

    # Contadores estilo Astrea
    nao_tratadas_hoje  = sum(1 for p in items if p.data_pub == hoje and p.status == 'pendente')
    tratadas_hoje      = sum(1 for p in items if p.data_pub == hoje and p.status == 'tratada')
    descartadas_hoje   = sum(1 for p in items if p.data_pub == hoje and p.status == 'descartada')
    total_nao_tratadas = sum(1 for p in items if p.status == 'pendente')

    return render_template('publicacoes.html',
        publicacoes       = items,
        processos         = processos,
        nao_tratadas_hoje = nao_tratadas_hoje,
        tratadas_hoje     = tratadas_hoje,
        descartadas_hoje  = descartadas_hoje,
        total_nao_tratadas= total_nao_tratadas,
    )


@bp.route('/nova', methods=['POST'])
def nova_publicacao():
    data_pub = datetime.strptime(request.form['data_pub'], '%Y-%m-%d').date()
    dias     = int(request.form.get('dias_prazo', 15))
    conteudo = request.form.get('conteudo', '')
    tem_efeito = detectar_efeito_intimatorio(conteudo)

    pub = Publicacao(
        data_pub               = data_pub,
        fonte                  = request.form.get('fonte'),
        tipo                   = request.form.get('tipo'),
        conteudo               = conteudo,
        dias_prazo             = dias,
        processo_id            = request.form.get('processo_id') or None,
        tem_efeito_intimatorio = tem_efeito,
        status                 = 'pendente',
    )
    db.session.add(pub)
    db.session.flush()

    prazo_venc_fmt = None
    if tem_efeito:
        data_venc = adicionar_dias_uteis(data_pub, dias)
        prazo_venc_fmt = data_venc.strftime('%d/%m/%Y')
        pr = Prazo(
            tipo        = f"Prazo – {request.form.get('tipo')}",
            descricao   = (
                f"Originado da publicação de {data_pub.strftime('%d/%m/%Y')}: "
                f"{conteudo[:120]}"
            ),
            data_inicio = data_pub,
            data_venc   = data_venc,
            dias        = dias,
            contagem    = 'Úteis',
            processo_id = request.form.get('processo_id') or None,
        )
        db.session.add(pr)
        db.session.flush()
        pub.prazo_gerado = True
        criar_tarefa_de_publicacao(pub, pr)

    db.session.commit()
    return jsonify({
        'ok':         True,
        'tem_efeito': tem_efeito,
        'prazo_venc': prazo_venc_fmt,
    })


@bp.route('/<int:id>/tratar', methods=['POST'])
def tratar_publicacao(id):
    pub = Publicacao.query.get_or_404(id)
    pub.status = 'tratada'
    db.session.commit()
    return jsonify({'ok': True})


@bp.route('/<int:id>/descartar', methods=['POST'])
def descartar_publicacao(id):
    pub = Publicacao.query.get_or_404(id)
    pub.status = 'descartada'

    # Marca tarefa vinculada como concluída (sem ação necessária)
    for t in pub.tarefas:
        if t.status != 'concluida':
            t.status       = 'concluida'
            t.concluida_em = datetime.utcnow()

    db.session.commit()
    return jsonify({'ok': True})


@bp.route('/importar-pje', methods=['POST'])
def importar_pje():
    data_ini = request.form.get('data_ini') or date.today().strftime('%Y-%m-%d')
    data_fim = request.form.get('data_fim') or date.today().strftime('%Y-%m-%d')
    try:
        resultado = importar_periodo(data_ini, data_fim)
        return jsonify({'ok': True, **resultado})
    except Exception as e:
        return jsonify({'ok': False, 'erro': str(e)})
