import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'castanheira-crm-2026')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER   = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB
    # Credenciais dos usuários (alterar senhas em produção)
    USERS = {
        'jardel':   {'senha': 'castanheira2026', 'nome': 'Dr. Jardel',  'perfil': 'advogado'},
        'steffany': {'senha': 'steffany2026',    'nome': 'Steffany',    'perfil': 'estagiaria'},
    }


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL')
        or f"sqlite:///{os.path.join(BASE_DIR, 'banco', 'castanheira.db')}"
    )


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL')
        or f"sqlite:///{os.path.join(BASE_DIR, 'banco', 'castanheira.db')}"
    )


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
