from datetime import datetime
from extensions import db


class Cliente(db.Model):
    id        = db.Column(db.Integer, primary_key=True)
    nome      = db.Column(db.String(200), nullable=False)
    cpf       = db.Column(db.String(20))
    telefone  = db.Column(db.String(30))
    email     = db.Column(db.String(120))
    endereco  = db.Column(db.String(300))
    obs       = db.Column(db.Text)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    processos = db.relationship('Processo', backref='cliente', lazy=True)
