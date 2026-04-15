from .dashboard import bp as dashboard_bp
from .clientes import bp as clientes_bp
from .processos import bp as processos_bp
from .publicacoes import bp as publicacoes_bp
from .prazos import bp as prazos_bp
from .tarefas import bp as tarefas_bp
from .api import bp as api_bp
from .andamentos import bp as andamentos_bp
from .financeiro import bp as financeiro_bp
from .documentos import bp as documentos_bp
from .auth import bp as auth_bp

__all__ = [
    'dashboard_bp', 'clientes_bp', 'processos_bp',
    'publicacoes_bp', 'prazos_bp', 'tarefas_bp', 'api_bp',
    'andamentos_bp', 'financeiro_bp', 'documentos_bp', 'auth_bp',
]
