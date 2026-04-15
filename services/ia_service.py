import anthropic

from extensions import db
from models import Tarefa

_SYSTEM_PROMPT = (
    "Você é assistente jurídico do Dr. Jardel Castanheira, advogado especialista em "
    "direito imobiliário em Papagaios/MG, processos em Divinópolis."
)


def gerar_sugestao(tarefa_id: int) -> str:
    """
    Consulta o Claude e salva a sugestão na tarefa.
    Retorna o texto gerado.
    Lança exceção em caso de erro na API.
    """
    t = Tarefa.query.get_or_404(tarefa_id)

    proc_info = (
        f"Processo: {t.processo.numero} — {t.processo.tipo}"
        if t.processo else "Sem processo vinculado"
    )
    prazo_fmt = t.prazo_data.strftime('%d/%m/%Y') if t.prazo_data else 'Não definido'

    client = anthropic.Anthropic()
    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=600,
        messages=[{
            "role": "user",
            "content": (
                f"{_SYSTEM_PROMPT}\n\n"
                f"Tarefa: {t.titulo}\n"
                f"Tipo: {t.tipo}\n"
                f"{proc_info}\n"
                f"Prazo: {prazo_fmt}\n"
                f"Descrição: {t.descricao or '(sem descrição)'}\n\n"
                "Dê orientação em 3-4 linhas: peça/ação correta, fundamento legal "
                "(CPC/CC/Lei), alerta estratégico. Seja direto como colega advogado sênior."
            ),
        }],
    )
    sugestao = msg.content[0].text
    t.ia_sugestao = sugestao
    db.session.commit()
    return sugestao
