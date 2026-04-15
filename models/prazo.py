from datetime import datetime, date
from extensions import db


class Prazo(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    tipo        = db.Column(db.String(100))
    descricao   = db.Column(db.Text)
    data_inicio = db.Column(db.Date)
    data_venc   = db.Column(db.Date, nullable=False)
    dias        = db.Column(db.Integer)
    contagem    = db.Column(db.String(20), default='Corridos')
    status      = db.Column(db.String(20), default='Pendente')
    processo_id   = db.Column(db.Integer, db.ForeignKey('processo.id'))
    publicacao_id = db.Column(db.Integer, db.ForeignKey('publicacao.id'), nullable=True)
    publicacao    = db.relationship('Publicacao', backref=db.backref('prazos_pub', lazy=True))
    criado_em     = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def dias_restantes(self):
        """Dias corridos até o vencimento (pode ser negativo se vencido)."""
        return (self.data_venc - date.today()).days

    @property
    def dias_uteis_restantes(self):
        """Dias úteis restantes (0 se vencido)."""
        from services.dias_uteis import dias_uteis_restantes
        dr = self.dias_restantes
        if dr <= 0:
            return dr
        return dias_uteis_restantes(self.data_venc)

    @property
    def urgencia(self):
        dr = self.dias_restantes
        if dr < 0:   return 'vencido'
        if dr == 0:  return 'urgente'
        # Para prazos em dias úteis: urgente ≤ 2 úteis, atenção ≤ 5 úteis
        if self.contagem == 'Úteis':
            du = self.dias_uteis_restantes
            if du <= 2: return 'urgente'
            if du <= 5: return 'atencao'
            return 'normal'
        # Prazos corridos: urgente ≤ 2 dias, atenção ≤ 7 dias
        if dr <= 2:  return 'urgente'
        if dr <= 7:  return 'atencao'
        return 'normal'
