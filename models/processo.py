from datetime import datetime
from extensions import db


class Processo(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    numero      = db.Column(db.String(50))
    tipo        = db.Column(db.String(100))
    polo        = db.Column(db.String(20), default='Autor')
    vara        = db.Column(db.String(100))
    comarca     = db.Column(db.String(100), default='Divinópolis')
    status      = db.Column(db.String(30), default='Ativo')
    obs         = db.Column(db.Text)
    cliente_id  = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    criado_em   = db.Column(db.DateTime, default=datetime.utcnow)
    publicacoes = db.relationship('Publicacao', backref='processo', lazy=True)
    prazos      = db.relationship('Prazo', backref='processo', lazy=True)
    tarefas     = db.relationship('Tarefa', backref='processo', lazy=True)
    andamentos  = db.relationship('Andamento', backref='processo', lazy=True,
                                  order_by='Andamento.data.desc()')
