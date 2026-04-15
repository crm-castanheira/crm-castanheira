from datetime import datetime, date
from extensions import db


class Tarefa(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    titulo       = db.Column(db.String(200), nullable=False)
    tipo         = db.Column(db.String(50))   # peticao, recurso, pesquisa, novo_caso, publicacao
    origem       = db.Column(db.String(50))   # whatsapp, ligacao, diario, pessoal, steffany
    descricao    = db.Column(db.Text)
    prioridade   = db.Column(db.String(20), default='normal')
    prazo_data   = db.Column(db.Date)
    status       = db.Column(db.String(20), default='pendente')  # pendente, em_andamento, concluida, cancelada
    responsavel  = db.Column(db.String(50), default='Jardel')    # Jardel | Steffany
    criado_por   = db.Column(db.String(50), default='Jardel')
    concluida_por= db.Column(db.String(50))
    processo_id  = db.Column(db.Integer, db.ForeignKey('processo.id'), nullable=True)
    ia_sugestao   = db.Column(db.Text)
    criado_em     = db.Column(db.DateTime, default=datetime.utcnow)
    concluida_em  = db.Column(db.DateTime)
    publicacao_id = db.Column(db.Integer, db.ForeignKey('publicacao.id'), nullable=True)
    publicacao    = db.relationship('Publicacao', backref=db.backref('tarefas', lazy=True))
    prazo_id      = db.Column(db.Integer, db.ForeignKey('prazo.id'), nullable=True)
    prazo_vinc    = db.relationship('Prazo', foreign_keys='Tarefa.prazo_id',
                                    backref=db.backref('tarefa_vinc', uselist=False))

    @property
    def atrasada(self) -> bool:
        """True se o prazo venceu e a tarefa ainda não foi concluída/cancelada."""
        return (
            self.prazo_data is not None
            and self.prazo_data < date.today()
            and self.status not in ('concluida', 'cancelada')
        )
