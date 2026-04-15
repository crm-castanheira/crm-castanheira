"""
Cálculo de dias úteis com base no calendário CPC.

Feriados fixos nacionais + feriados móveis calculados a partir da Páscoa
para o intervalo 2024-2030.
"""
from datetime import date, timedelta


# ── Feriados fixos (mês, dia) ────────────────────────────────────────────────
_FIXOS = {
    (1,  1),   # Ano Novo
    (4, 21),   # Tiradentes
    (5,  1),   # Dia do Trabalho
    (9,  7),   # Independência do Brasil
    (10,12),   # Nossa Senhora Aparecida
    (11, 2),   # Finados
    (11,15),   # Proclamação da República
    (11,20),   # Consciência Negra (Lei 14.759/2023)
    (12,25),   # Natal
}


def _pascoa(ano: int) -> date:
    """Algoritmo de Butcher/Meeus para calcular a Páscoa."""
    a = ano % 19
    b, c = divmod(ano, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19*a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2*e + 2*i - h - k) % 7
    m = (a + 11*h + 22*l) // 451
    mes, dia = divmod(114 + h + l - 7*m, 31)
    return date(ano, mes, dia + 1)


def _feriados_ano(ano: int) -> set:
    feriados = {date(ano, m, d) for m, d in _FIXOS}

    pascoa      = _pascoa(ano)
    feriados.add(pascoa - timedelta(days=48))  # 2ª Carnaval
    feriados.add(pascoa - timedelta(days=47))  # 3ª Carnaval
    feriados.add(pascoa - timedelta(days=2))   # Sexta-feira Santa
    feriados.add(pascoa)                        # Páscoa
    feriados.add(pascoa + timedelta(days=60))  # Corpus Christi

    return feriados


# Cache de feriados por ano
_cache: dict[int, set] = {}


def _get_feriados(ano: int) -> set:
    if ano not in _cache:
        _cache[ano] = _feriados_ano(ano)
    return _cache[ano]


def eh_dia_util(d: date) -> bool:
    """Retorna True se 'd' for dia útil (não é fim de semana nem feriado)."""
    if d.weekday() >= 5:   # 5=Sábado, 6=Domingo
        return False
    return d not in _get_feriados(d.year)


def adicionar_dias_uteis(inicio: date, n: int) -> date:
    """
    Retorna a data que resulta de adicionar 'n' dias úteis a 'inicio'.
    O dia 'inicio' não é contado; a contagem começa no próximo dia útil.
    """
    atual = inicio
    contados = 0
    while contados < n:
        atual += timedelta(days=1)
        if eh_dia_util(atual):
            contados += 1
    return atual


def dias_uteis_restantes(ate: date) -> int:
    """Conta os dias úteis entre hoje (exclusive) e 'ate' (inclusive)."""
    hoje  = date.today()
    if ate <= hoje:
        return (ate - hoje).days  # negativo ou zero — contagem corrida p/ urgência
    atual = hoje
    count = 0
    while atual < ate:
        atual += timedelta(days=1)
        if eh_dia_util(atual):
            count += 1
    return count


# Mapeamento tipo-de-ato → (dias, contagem)
# Fonte: CPC art. 219, 1003, 1003§5, etc.
PRAZOS_CPC: dict[str, tuple[int, str]] = {
    'contestação':           (15, 'Úteis'),
    'contestacao':           (15, 'Úteis'),
    'apelação':              (15, 'Úteis'),
    'apelacao':              (15, 'Úteis'),
    'agravo de instrumento': (15, 'Úteis'),
    'agravo regimental':     (15, 'Úteis'),
    'réplica':               (15, 'Úteis'),
    'replica':               (15, 'Úteis'),
    'cumprimento':           (15, 'Úteis'),
    'embargos à execução':   (15, 'Úteis'),
    'embargos a execucao':   (15, 'Úteis'),
    'embargos de declaração':(5,  'Úteis'),
    'embargos de declaracao':(5,  'Úteis'),
}


def prazo_para_tipo(tipo_ato: str) -> tuple[int, str]:
    """
    Retorna (dias, contagem) para um tipo de ato processual.
    Fallback: (15, 'Úteis').
    """
    chave = tipo_ato.lower().strip()
    return PRAZOS_CPC.get(chave, (15, 'Úteis'))
