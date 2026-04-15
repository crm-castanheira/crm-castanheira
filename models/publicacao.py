from datetime import datetime
from extensions import db


class Publicacao(db.Model):
    id                    = db.Column(db.Integer, primary_key=True)
    data_pub              = db.Column(db.Date, nullable=False)   # data de publicação (contagem de prazo)
    data_divulgacao       = db.Column(db.Date, nullable=True)    # data de divulgação no DJ (pode ser D-1)
    fonte                 = db.Column(db.String(80))
    tipo                  = db.Column(db.String(80))
    conteudo              = db.Column(db.Text)
    dias_prazo            = db.Column(db.Integer, default=15)
    processo_id           = db.Column(db.Integer, db.ForeignKey('processo.id'))
    prazo_gerado          = db.Column(db.Boolean, default=False)
    # status de tratamento pelo advogado
    status                = db.Column(db.String(20), default='pendente')  # pendente | tratada | descartada
    tem_efeito_intimatorio = db.Column(db.Boolean, default=True)          # False = não gera prazo/tarefa
    criado_em             = db.Column(db.DateTime, default=datetime.utcnow)
    # campos PJe
    pje_id                = db.Column(db.Integer, unique=True, nullable=True)
    pje_tribunal          = db.Column(db.String(20), nullable=True)
    pje_link              = db.Column(db.String(500), nullable=True)
    pje_numero            = db.Column(db.String(50), nullable=True)
