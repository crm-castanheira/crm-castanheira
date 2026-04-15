from datetime import datetime
from extensions import db


class Comentario(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    tarefa_id   = db.Column(db.Integer, db.ForeignKey('tarefa.id'), nullable=False)
    texto       = db.Column(db.Text, nullable=False)
    tipo        = db.Column(db.String(20), default='comentario')   # comentario | subtarefa
    responsavel = db.Column(db.String(50), default='Jardel')
    prazo_data  = db.Column(db.Date, nullable=True)
    autor       = db.Column(db.String(50), default='Jardel')
    criado_em   = db.Column(db.DateTime, default=datetime.utcnow)
    concluido   = db.Column(db.Boolean, default=False)
