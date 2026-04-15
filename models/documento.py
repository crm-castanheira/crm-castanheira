from datetime import datetime
from extensions import db


class Documento(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    nome_arquivo = db.Column(db.String(255), nullable=False)   # nome original exibido
    caminho      = db.Column(db.String(512), nullable=False)   # caminho em disco (uuid_nome)
    descricao    = db.Column(db.String(300))
    tipo         = db.Column(db.String(50))   # peticao, recurso, contrato, procuracao, decisao, sentenca, certidao, outro
    responsavel  = db.Column(db.String(50), default='Jardel')
    processo_id  = db.Column(db.Integer, db.ForeignKey('processo.id'), nullable=True)
    tarefa_id    = db.Column(db.Integer, db.ForeignKey('tarefa.id'), nullable=True)
    criado_em    = db.Column(db.DateTime, default=datetime.utcnow)

    processo = db.relationship('Processo', backref=db.backref('documentos', lazy=True))
    tarefa   = db.relationship('Tarefa',   backref=db.backref('documentos', lazy=True))

    @property
    def extensao(self) -> str:
        parts = self.nome_arquivo.rsplit('.', 1)
        return parts[1].lower() if len(parts) == 2 else ''

    @property
    def icone(self) -> str:
        ext = self.extensao
        if ext == 'pdf':
            return '📄'
        if ext in ('doc', 'docx'):
            return '📝'
        if ext in ('xls', 'xlsx'):
            return '📊'
        if ext in ('jpg', 'jpeg', 'png', 'gif'):
            return '🖼'
        return '📎'
