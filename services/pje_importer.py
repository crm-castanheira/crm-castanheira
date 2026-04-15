import re
import html as html_lib
from datetime import datetime, timedelta

import httpx

from extensions import db
from models import Publicacao, Processo, Prazo
from services.publicacao_service import criar_tarefa_de_publicacao, detectar_efeito_intimatorio

PJE_API = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"
OAB_NUM = "183408"
OAB_UF  = "MG"


def _strip_html(texto: str) -> str:
    """Remove tags HTML (incluindo style/script), decodifica entidades e normaliza espaços."""
    texto = html_lib.unescape(texto or '')
    texto = re.sub(
        r'<(style|script|head)[^>]*>.*?</(style|script|head)>',
        ' ', texto, flags=re.DOTALL | re.IGNORECASE
    )
    texto = re.sub(r'<[^>]+>', ' ', texto)
    return re.sub(r'\s+', ' ', texto).strip()


def _dias_prazo_por_tipo(tipo_doc: str) -> int:
    tipo = (tipo_doc or '').lower()
    if 'senten' in tipo or 'acord' in tipo:
        return 15
    if 'decis' in tipo:
        return 15
    if 'cita' in tipo:
        return 15
    return 15  # default


def importar_periodo(data_ini: str, data_fim: str) -> dict:
    """
    Consulta a API PJe e importa publicações do período informado.
    Retorna dict com chaves: importadas, duplicadas, erros, total_api.
    Lança exceção em caso de falha de rede.
    """
    importadas = 0
    duplicadas = 0
    erros      = 0
    pagina     = 1

    while True:
        resp = httpx.get(PJE_API, params={
            'pagina': pagina,
            'itensPorPagina': 50,
            'dataDisponibilizacaoInicio': data_ini,
            'dataDisponibilizacaoFim':    data_fim,
            'numeroOab': OAB_NUM,
            'ufOab':     OAB_UF,
        }, timeout=20)
        resp.raise_for_status()
        dados = resp.json()
        itens = dados.get('items', [])
        if not itens:
            break

        for item in itens:
            pje_id = item.get('id')
            if Publicacao.query.filter_by(pje_id=pje_id).first():
                duplicadas += 1
                continue

            try:
                data_pub = datetime.strptime(
                    item['data_disponibilizacao'], '%Y-%m-%d'
                ).date()
                tipo_doc = item.get('tipoComunicacao') or item.get('tipoDocumento') or 'Intimação'
                tribunal = item.get('siglaTribunal', '')
                num_proc = item.get('numeroprocessocommascara') or item.get('numero_processo', '')
                conteudo = _strip_html(item.get('texto', ''))[:2000]
                dias     = _dias_prazo_por_tipo(tipo_doc)

                proc_id = None
                if num_proc:
                    proc = Processo.query.filter(
                        Processo.numero.contains(num_proc[:20])
                    ).first()
                    if proc:
                        proc_id = proc.id

                tem_efeito = detectar_efeito_intimatorio(conteudo)

                pub = Publicacao(
                    data_pub               = data_pub,
                    fonte                  = f"PJe – {tribunal}",
                    tipo                   = tipo_doc,
                    conteudo               = conteudo,
                    dias_prazo             = dias,
                    processo_id            = proc_id,
                    pje_id                 = pje_id,
                    pje_tribunal           = tribunal,
                    pje_link               = item.get('link'),
                    pje_numero             = num_proc,
                    tem_efeito_intimatorio = tem_efeito,
                    status                 = 'pendente',
                )
                db.session.add(pub)
                db.session.flush()

                if tem_efeito:
                    data_venc = data_pub + timedelta(days=dias)
                    pr = Prazo(
                        tipo        = f"Prazo – {tipo_doc}",
                        descricao   = f"[PJe/{tribunal}] {num_proc} — {conteudo[:120]}",
                        data_inicio = data_pub,
                        data_venc   = data_venc,
                        dias        = dias,
                        processo_id = proc_id,
                    )
                    db.session.add(pr)
                    db.session.flush()
                    pub.prazo_gerado = True
                    criar_tarefa_de_publicacao(pub, pr)
                importadas += 1
            except Exception:
                erros += 1

        db.session.commit()

        total = dados.get('count', 0)
        if pagina * 50 >= total:
            break
        pagina += 1

    return {
        'importadas': importadas,
        'duplicadas': duplicadas,
        'erros':      erros,
        'total_api':  importadas + duplicadas + erros,
    }
