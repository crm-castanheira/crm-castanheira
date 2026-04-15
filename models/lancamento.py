from datetime import datetime, date
from extensions import db


class Lancamento(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    tipo            = db.Column(db.String(10), nullable=False)   # receber | pagar
    descricao       = db.Column(db.String(200), nullable=False)
    valor           = db.Column(db.Float, nullable=False)
    data_venc       = db.Column(db.Date, nullable=False)
    data_pagamento  = db.Column(db.Date)
    status          = db.Column(db.String(20), default='pendente')  # pendente | pago | cancelado
    categoria       = db.Column(db.String(50))
    processo_id     = db.Column(db.Integer, db.ForeignKey('processo.id'), nullable=True)
    cliente_id      = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=True)
    criado_em       = db.Column(db.DateTime, default=datetime.utcnow)

    processo = db.relationship('Processo', backref=db.backref('lancamentos', lazy=True))
    cliente  = db.relationship('Cliente',  backref=db.backref('lancamentos', lazy=True))

    @property
    def atrasado(self) -> bool:
        return self.status == 'pendente' and self.data_venc < date.today()

    @property
    def dias_restantes(self) -> int:
        return (self.data_venc - date.today()).days
