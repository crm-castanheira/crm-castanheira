import csv
import io
from datetime import datetime, date

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, Response

from extensions import db
from models import Prazo, Processo

bp = Blueprint('prazos', __name__, url_prefix='/prazos')


@bp.route('/')
def prazos():
    hoje   = date.today()
    q      = request.args.get('q', '').strip()
    status = request.args.get('status', '')
    tipo   = request.args.get('tipo', '').strip()
    de     = request.args.get('de', '')
    ate    = request.args.get('ate', '')

    # Base: todos os não-cumpridos (Pendente + Vencido virtual)
    query = Prazo.query

    if status == 'Cumprido':
        query = query.filter_by(status='Cumprido')
    elif status == 'Vencido':
        query = query.filter(Prazo.status == 'Pendente', Prazo.data_venc < hoje)
    elif status == 'Pendente':
        query = query.filter(Prazo.status == 'Pendente', Prazo.data_venc >= hoje)
    else:
        # Padrão: pendentes (inclui vencidos não cumpridos)
        query = query.filter(Prazo.status == 'Pendente')

    if tipo:
        query = query.filter(Prazo.tipo.ilike(f'%{tipo}%'))

    if q:
        query = query.join(Processo, Prazo.processo_id == Processo.id, isouter=True).filter(
            db.or_(
                Processo.numero.ilike(f'%{q}%'),
                Processo.tipo.ilike(f'%{q}%'),
            )
        )

    if de:
        query = query.filter(Prazo.data_venc >= de)
    if ate:
        query = query.filter(Prazo.data_venc <= ate)

    todos = sorted(query.all(), key=lambda p: p.data_venc)

    # Métricas para os cards do topo
    pendentes_todos = Prazo.query.filter_by(status='Pendente').all()
    urgentes   = [p for p in pendentes_todos if p.urgencia in ('urgente',) and p.dias_restantes >= 0]
    vencidos   = [p for p in pendentes_todos if p.dias_restantes < 0]
    semana     = [p for p in pendentes_todos if 0 <= p.dias_restantes <= 7]

    cumpridos = (
        Prazo.query
        .filter_by(status='Cumprido')
        .order_by(Prazo.data_cumprimento.desc(), Prazo.data_venc.desc())
        .limit(20).all()
    )

    return render_template('prazos.html',
        prazos    = todos,
        cumpridos = cumpridos,
        hoje      = hoje,
        urgentes  = len(urgentes),
        vencidos  = len(vencidos),
        semana    = len(semana),
        q=q, status=status, tipo=tipo, de=de, ate=ate,
    )


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
            origem      = 'manual',
        )
        db.session.add(pr)
        db.session.commit()
        return redirect(url_for('prazos.prazos'))
    return render_template('form_prazo.html', processos=processos)


@bp.route('/<int:id>/cumprir', methods=['POST'])
def cumprir_prazo(id):
    p = Prazo.query.get_or_404(id)
    data = request.get_json(silent=True) or {}
    p.status = 'Cumprido'
    p.data_cumprimento = date.today()
    if data.get('obs'):
        p.obs_cumprimento = data['obs'].strip()
    if data.get('data_cumprimento'):
        try:
            p.data_cumprimento = datetime.strptime(data['data_cumprimento'], '%Y-%m-%d').date()
        except ValueError:
            pass
    db.session.commit()
    return jsonify({'ok': True})


@bp.route('/exportar')
def exportar_prazos():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Tipo', 'Processo', 'Cliente', 'Vencimento', 'Dias Restantes', 'Status', 'Origem', 'Observação'])

    prazos = Prazo.query.order_by(Prazo.data_venc).all()
    for p in prazos:
        writer.writerow([
            p.tipo,
            p.processo.numero if p.processo else '',
            p.processo.cliente.nome if p.processo and p.processo.cliente else '',
            p.data_venc.strftime('%d/%m/%Y'),
            p.dias_restantes,
            p.status,
            getattr(p, 'origem', 'manual'),
            p.obs_cumprimento or '',
        ])

    return Response(
        output.getvalue(),
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename=prazos_castanheira.csv'},
    )
