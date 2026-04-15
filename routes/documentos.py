import os
import uuid

from flask import Blueprint, current_app, redirect, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from extensions import db
from models.documento import Documento

bp = Blueprint('documentos', __name__)

EXTENSOES_PERMITIDAS = {
    'pdf', 'doc', 'docx', 'xls', 'xlsx',
    'jpg', 'jpeg', 'png', 'gif', 'txt', 'odt', 'ods',
}


def _extensao_ok(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS


@bp.route('/processos/<int:processo_id>/documentos', methods=['POST'])
def upload_processo(processo_id):
    arquivo = request.files.get('arquivo')
    if not arquivo or arquivo.filename == '':
        return redirect(url_for('processos.ver_processo', id=processo_id) + '#documentos')

    nome_original = arquivo.filename
    if not _extensao_ok(nome_original):
        return redirect(url_for('processos.ver_processo', id=processo_id) + '#documentos')

    nome_seguro  = secure_filename(nome_original)
    nome_disco   = f"{uuid.uuid4().hex}_{nome_seguro}"
    pasta        = current_app.config['UPLOAD_FOLDER']
    os.makedirs(pasta, exist_ok=True)
    arquivo.save(os.path.join(pasta, nome_disco))

    doc = Documento(
        nome_arquivo = nome_original,
        caminho      = nome_disco,
        descricao    = request.form.get('descricao', '').strip() or None,
        tipo         = request.form.get('tipo', 'outro'),
        responsavel  = request.form.get('responsavel', 'Jardel'),
        processo_id  = processo_id,
    )
    db.session.add(doc)
    db.session.commit()
    return redirect(url_for('processos.ver_processo', id=processo_id) + '#documentos')


@bp.route('/documentos/<int:id>/download')
def download(id):
    doc   = Documento.query.get_or_404(id)
    pasta = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(pasta, doc.caminho, as_attachment=True,
                               download_name=doc.nome_arquivo)


@bp.route('/documentos/<int:id>/excluir', methods=['POST'])
def excluir(id):
    doc         = Documento.query.get_or_404(id)
    processo_id = doc.processo_id
    # Remove arquivo do disco
    try:
        caminho = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.caminho)
        if os.path.exists(caminho):
            os.remove(caminho)
    except OSError:
        pass
    db.session.delete(doc)
    db.session.commit()
    if processo_id:
        return redirect(url_for('processos.ver_processo', id=processo_id) + '#documentos')
    return redirect('/')
