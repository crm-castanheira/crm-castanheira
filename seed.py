"""
Seed — 28 processos reais de Castanheira e Reis Advogados Associados.

Como usar:
    python seed.py

O script é idempotente: verifica pelo número do processo antes de inserir.
Preencha os dados reais nas listas CLIENTES e PROCESSOS abaixo.
"""
import os
import sys

# Garante que o app pode ser importado de qualquer diretório
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from extensions import db
from models import Cliente, Processo

# ── Dados reais ──────────────────────────────────────────────────────────────
# Preencha com os clientes reais do escritório.
# 'ref' é uma chave interna usada para vincular processos.
CLIENTES = [
    # {'ref': 'cli1', 'nome': 'Maria Aparecida Silva',      'cpf': '000.000.000-00', 'telefone': '(37) 9 0000-0000', 'email': '', 'endereco': 'Divinópolis/MG'},
    # {'ref': 'cli2', 'nome': 'João Carlos Ferreira',       'cpf': '000.000.000-00', 'telefone': '(37) 9 0000-0000', 'email': '', 'endereco': 'Divinópolis/MG'},
    # Adicione os demais clientes aqui...
]

# Preencha com os 28 processos reais.
# 'cliente_ref' deve bater com o 'ref' definido em CLIENTES (ou None).
PROCESSOS = [
    # {
    #     'numero':      '0001234-00.2023.8.13.0220',
    #     'tipo':        'Ação de Execução de Título Extrajudicial',
    #     'polo':        'Autor',          # Autor | Réu
    #     'vara':        '2ª Vara Cível',
    #     'comarca':     'Divinópolis',
    #     'status':      'Ativo',          # Ativo | Arquivado | Suspenso
    #     'obs':         '',
    #     'cliente_ref': 'cli1',
    # },
    # {
    #     'numero':      '0005678-00.2022.8.13.0220',
    #     'tipo':        'Ação de Usucapião',
    #     'polo':        'Autor',
    #     'vara':        '1ª Vara Cível',
    #     'comarca':     'Pitangui',
    #     'status':      'Ativo',
    #     'obs':         '',
    #     'cliente_ref': 'cli2',
    # },
    # ... adicione até completar os 28 processos
]
# ─────────────────────────────────────────────────────────────────────────────


def run():
    app = create_app()
    with app.app_context():
        # Mapeia ref → id de cliente
        refs: dict[str, int] = {}
        for dados in CLIENTES:
            ref = dados.pop('ref')
            existe = Cliente.query.filter_by(nome=dados['nome']).first()
            if existe:
                refs[ref] = existe.id
                print(f"  [skip] Cliente já existe: {dados['nome']}")
            else:
                c = Cliente(**dados)
                db.session.add(c)
                db.session.flush()
                refs[ref] = c.id
                print(f"  [+] Cliente inserido: {dados['nome']}")

        inseridos = 0
        pulados   = 0
        for dados in PROCESSOS:
            ref_cli = dados.pop('cliente_ref', None)
            dados['cliente_id'] = refs.get(ref_cli) if ref_cli else None

            existe = Processo.query.filter_by(numero=dados['numero']).first()
            if existe:
                pulados += 1
                print(f"  [skip] Processo já existe: {dados['numero']}")
            else:
                p = Processo(**dados)
                db.session.add(p)
                inseridos += 1
                print(f"  [+] Processo inserido: {dados['numero']}")

        db.session.commit()
        print(f"\nConcluído: {inseridos} processos inseridos, {pulados} pulados.")


if __name__ == '__main__':
    run()
