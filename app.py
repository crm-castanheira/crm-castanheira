import os

from flask import Flask

from config import config
from extensions import db


def create_app(env: str = None) -> Flask:
    env = env or os.environ.get('FLASK_ENV', 'default')
    app = Flask(__name__)
    app.config.from_object(config[env])

    os.makedirs(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'banco'), exist_ok=True)
    os.makedirs(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads'), exist_ok=True)

    db.init_app(app)
    app.url_map.strict_slashes = False

    # Importa modelos para que o SQLAlchemy os registre antes do create_all
    import models  # noqa: F401

    # Blueprints
    from routes import (
        dashboard_bp, clientes_bp, processos_bp,
        publicacoes_bp, prazos_bp, tarefas_bp, api_bp,
        andamentos_bp, financeiro_bp, documentos_bp, auth_bp,
    )
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(clientes_bp)
    app.register_blueprint(processos_bp)
    app.register_blueprint(publicacoes_bp)
    app.register_blueprint(prazos_bp)
    app.register_blueprint(tarefas_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(andamentos_bp)
    app.register_blueprint(financeiro_bp)
    app.register_blueprint(documentos_bp)

    # Proteção global: redireciona para login se não autenticado
    from flask import session, redirect, url_for, request as _req

    @app.before_request
    def requer_login():
        rotas_publicas = {'auth.login', 'auth.logout', 'static'}
        if _req.endpoint and _req.endpoint not in rotas_publicas:
            if 'usuario' not in session:
                return redirect(url_for('auth.login', next=_req.url))

    # Injeta usuário atual em todos os templates
    @app.context_processor
    def inject_usuario():
        return {
            'usuario_atual': session.get('nome', ''),
            'usuario_perfil': session.get('perfil', ''),
        }

    with app.app_context():
        db.create_all()
        _migrar_banco(db)
        _retroativo_publicacoes()

    return app


def _migrar_banco(db):
    """Aplica migrações de colunas novas em bancos existentes."""
    with db.engine.connect() as conn:
        colunas = {
            'tarefa': [
                ("publicacao_id",          "INTEGER REFERENCES publicacao(id)"),
                ("prazo_id",               "INTEGER REFERENCES prazo(id)"),
                ("responsavel",            "VARCHAR(50) DEFAULT 'Jardel'"),
                ("criado_por",             "VARCHAR(50) DEFAULT 'Jardel'"),
                ("concluida_por",          "VARCHAR(50)"),
            ],
            'prazo': [
                ("publicacao_id",          "INTEGER REFERENCES publicacao(id)"),
            ],
            'publicacao': [
                ("status",                 "VARCHAR(20) DEFAULT 'pendente'"),
                ("tem_efeito_intimatorio", "BOOLEAN DEFAULT 1"),
                ("data_divulgacao",        "DATE"),
            ],
        }
        for tabela, novas_cols in colunas.items():
            existentes = {row[1] for row in conn.execute(
                db.text(f"PRAGMA table_info({tabela})")
            )}
            for col, tipo in novas_cols:
                if col not in existentes:
                    conn.execute(db.text(
                        f"ALTER TABLE {tabela} ADD COLUMN {col} {tipo}"
                    ))
        conn.commit()

    # Retroativo: detecta efeito intimatório nas publicações existentes
    _retroativo_efeito_intimatorio()


def _retroativo_publicacoes():
    """
    Para publicações existentes sem tarefa vinculada:
      1. Tenta ligar o prazo à publicação (melhor match por data + processo).
      2. Cria a tarefa de análise usando o serviço padrão.
    Idempotente: ignora publicações que já têm tarefa.
    """
    from models import Publicacao, Prazo, Tarefa
    from services.publicacao_service import criar_tarefa_de_publicacao

    pubs_sem_tarefa = (
        Publicacao.query
        .filter(~Publicacao.tarefas.any())
        .order_by(Publicacao.data_pub)
        .all()
    )

    if not pubs_sem_tarefa:
        return

    for pub in pubs_sem_tarefa:
        # Tenta encontrar o prazo correspondente pelo heurístico:
        # mesma data de início, mesmo processo, publicacao_id ainda não vinculado
        q = Prazo.query.filter(
            Prazo.data_inicio == pub.data_pub,
            Prazo.publicacao_id.is_(None),
        )
        if pub.processo_id:
            q = q.filter(Prazo.processo_id == pub.processo_id)
        prazo = q.first()

        criar_tarefa_de_publicacao(pub, prazo)

    db.session.commit()


def _retroativo_efeito_intimatorio():
    """
    Para publicações existentes, detecta automaticamente se têm efeito
    intimatório com base no conteúdo. Idempotente.
    """
    from models import Publicacao
    from services.publicacao_service import detectar_efeito_intimatorio

    pubs = Publicacao.query.all()
    for pub in pubs:
        novo_valor = detectar_efeito_intimatorio(pub.conteudo)
        if pub.tem_efeito_intimatorio != novo_valor:
            pub.tem_efeito_intimatorio = novo_valor
    db.session.commit()


if __name__ == '__main__':
    create_app().run(debug=True, port=5000)
