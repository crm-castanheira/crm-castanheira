from datetime import datetime
from extensions import db

PALAVRAS_IMPORTANTE = {
    'intimação', 'intimacao', 'prazo', 'sentença', 'sentenca',
    'decisão', 'decisao', 'despacho', 'citação', 'citacao',
    'penhora', 'leilão', 'leilao', 'arresto',
}


def classificar_importante(descricao: str) -> bool:
    texto = descricao.lower()
    return any(p in texto for p in PALAVRAS_IMPORTANTE)


class Andamento(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    processo_id = db.Column(db.Integer, db.ForeignKey('processo.id'), nullable=False)
    data        = db.Column(db.Date, nullable=False)
    descricao   = db.Column(db.Text, nullable=False)
    importante  = db.Column(db.Boolean, default=False)
    origem      = db.Column(db.String(20), default='manual')  # manual | pje
    criado_em   = db.Column(db.DateTime, default=datetime.utcnow)
