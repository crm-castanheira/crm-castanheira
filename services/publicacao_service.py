"""
Lógica de negócio relacionada a publicações.

Toda publicação COM efeito intimatório gera prazo + tarefa automaticamente.
Publicações SEM efeito intimatório apenas ficam como "pendente" para ciência
do advogado — não geram prazo nem tarefa.
"""
from typing import Optional

from extensions import db
from models.tarefa import Tarefa
from services.dias_uteis import adicionar_dias_uteis

# Padrões que indicam publicação SEM efeito intimatório
_PADROES_SEM_EFEITO = (
    'sem efeito intimatório',
    'sem efeito intimatorio',
    'publicações sem efeito',
    'publicacoes sem efeito',
    'publicação sem efeito',
    'publicacao sem efeito',
    'sem efeito de intimação',
    'sem efeito de intimacao',
)


def detectar_efeito_intimatorio(conteudo: str) -> bool:
    """
    Retorna True se a publicação TEM efeito intimatório (gera prazo).
    Retorna False se contiver padrão de 'sem efeito intimatório'.
    """
    texto = (conteudo or '').lower()
    return not any(p in texto for p in _PADROES_SEM_EFEITO)


def criar_tarefa_de_publicacao(pub, prazo=None) -> Optional[Tarefa]:
    """
    Cria e persiste uma Tarefa vinculada à publicação recebida.

    Retorna None se a publicação não tiver efeito intimatório
    (nesse caso não há ação a tomar — apenas ciência).

    Deve ser chamado após db.session.flush() tanto na publicação quanto
    no prazo (para que pub.id e prazo.id já estejam disponíveis),
    dentro da mesma transação.
    """
    if not pub.tem_efeito_intimatorio:
        return None

    origem     = 'pje' if pub.pje_id else 'diario'
    referencia = pub.pje_numero or (pub.processo.numero if pub.processo else pub.fonte)
    titulo     = f"Analisar {pub.tipo}: {referencia}"[:200]
    prazo_dt   = adicionar_dias_uteis(pub.data_pub, pub.dias_prazo)

    descricao_pub = (pub.conteudo or '').strip()
    descricao = (
        f"Publicação de {pub.data_pub.strftime('%d/%m/%Y')} "
        f"— {pub.pje_tribunal or pub.fonte}.\n\n"
        f"{descricao_pub[:500]}{'…' if len(descricao_pub) > 500 else ''}"
    )

    t = Tarefa(
        titulo        = titulo,
        tipo          = 'publicacao',
        origem        = origem,
        descricao     = descricao,
        prioridade    = 'normal',
        prazo_data    = prazo_dt,
        processo_id   = pub.processo_id,
        publicacao_id = pub.id,
        prazo_id      = prazo.id if prazo else None,
    )
    db.session.add(t)

    if prazo and prazo.publicacao_id is None:
        prazo.publicacao_id = pub.id

    return t
