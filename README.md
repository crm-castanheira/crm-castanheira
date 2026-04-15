# CRM Castanheira
## Sistema de Gestão Jurídica — v1.1

**Dr. Jardel Sousa Castanheira Costa** · OAB/MG 183408  
Direito Imobiliário · Papagaios/MG · Processos em Divinópolis/MG

---

## Funcionalidades

| Módulo | O que faz |
|---|---|
| **Dashboard** | Visão geral: prazos urgentes, tarefas abertas, publicações pendentes |
| **Clientes** | Cadastro com CPF, telefone, e-mail, endereço e observações |
| **Processos** | Vinculados a clientes; controla número CNJ, vara, comarca, polo e status |
| **Publicações** | Registro manual + **importação automática do PJe** com lançamento de prazo |
| **Prazos** | Gerados automaticamente por publicação; alertas vencido / urgente (≤2d) / atenção (≤7d) |
| **Tarefas** | Controle de demandas com tipo, origem, prioridade e sugestão de IA |
| **IA Jurídica** | Integração com Claude (Anthropic) para orientação jurídica por tarefa |

---

## Como instalar e iniciar

### Windows

1. Instale o Python 3.8+ em https://python.org  
   (marque "Add Python to PATH" durante a instalação)
2. Clique duas vezes em `iniciar_windows.bat`
3. Acesse: `http://localhost:5000`

### macOS / Linux

```bash
bash instalar.sh        # apenas na primeira vez
source venv/bin/activate
python app.py
```

Acesse: `http://localhost:5000`

### Acesso pelo celular

Com o servidor rodando, descubra o IP do computador (`ipconfig` no Windows / `ifconfig` no Mac) e acesse `http://192.168.X.X:5000` na mesma rede Wi-Fi.

---

## IA Jurídica (opcional)

Para usar o botão **✨ IA** nas tarefas:

1. Crie conta e gere uma API Key em https://console.anthropic.com
2. Configure antes de iniciar o servidor:

```bash
# Mac/Linux
export ANTHROPIC_API_KEY="sk-ant-..."
python app.py
```

```bat
:: Windows
set ANTHROPIC_API_KEY=sk-ant-...
python app.py
```

---

## Integração PJe

O sistema consome a API pública do **Portal de Comunicações Processuais (PJe/CNJ)**:

```
GET https://comunicaapi.pje.jus.br/api/v1/comunicacao
    ?numeroOab=183408
    &ufOab=MG
    &dataDisponibilizacaoInicio=YYYY-MM-DD
    &dataDisponibilizacaoFim=YYYY-MM-DD
    &pagina=1
    &itensPorPagina=50
```

- API aberta, sem autenticação
- Traz comunicações de todos os tribunais (TJMG, TRT3, STJ etc.)
- Importação **idempotente**: registros já importados (por `pje_id`) são ignorados
- Cada publicação gera um **prazo de 15 dias** automaticamente
- Conteúdo HTML é limpo (remove `<style>`, `<script>`, tags) antes de salvar

Na tela de Publicações, clique em **⬇ Importar PJe**, escolha o período e confirme.

---

## Stack tecnológica

| Camada | Tecnologia |
|---|---|
| Backend | Python 3 + Flask |
| ORM / Banco | SQLAlchemy + SQLite (`banco/castanheira.db`) |
| HTTP client | httpx |
| IA | Anthropic Python SDK (Claude claude-opus-4-5) |
| Frontend | Jinja2 + HTML/CSS/JS puro (sem framework JS) |

O banco SQLite é criado automaticamente na primeira execução.  
**Backup:** basta copiar o arquivo `banco/castanheira.db`.

### Migrações manuais de banco

O projeto não usa ferramenta de migração. Para adicionar colunas ao banco existente:

```bash
sqlite3 banco/castanheira.db "ALTER TABLE nome_tabela ADD COLUMN nova_coluna TIPO;"
```

---

## Rotas disponíveis

| Método | Rota | Descrição |
|---|---|---|
| GET | `/` | Dashboard |
| GET | `/clientes` | Lista clientes |
| GET/POST | `/clientes/novo` | Cadastrar cliente |
| GET | `/processos` | Lista processos |
| GET/POST | `/processos/novo` | Cadastrar processo |
| GET | `/processos/<id>` | Detalhe do processo |
| GET | `/prazos` | Lista prazos pendentes |
| GET/POST | `/prazos/novo` | Cadastrar prazo manualmente |
| POST | `/prazos/<id>/cumprir` | Marcar prazo como cumprido |
| GET | `/publicacoes` | Lista publicações |
| POST | `/publicacoes/nova` | Registrar publicação manual |
| POST | `/publicacoes/importar-pje` | Importar do PJe por período |
| GET | `/tarefas` | Lista tarefas |
| POST | `/tarefas/nova` | Criar tarefa |
| POST | `/tarefas/<id>/concluir` | Concluir tarefa |
| POST | `/tarefas/<id>/ia` | Gerar sugestão da IA para tarefa |
| GET | `/api/resumo` | JSON com resumo geral do escritório |

---

## Estrutura atual

O projeto está em **arquivo único** (`app.py`) — modelos, rotas e lógica juntos, adequado para o escopo atual.

```
crm_castanheira/
├── app.py                  # Toda a aplicação (modelos + rotas + lógica)
├── banco/
│   └── castanheira.db      # Banco SQLite (criado automaticamente)
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── clientes.html / form_cliente.html
│   ├── processos.html / form_processo.html / ver_processo.html
│   ├── publicacoes.html
│   ├── prazos.html / form_prazo.html
│   └── tarefas.html
├── venv/
├── instalar.sh
├── iniciar_windows.bat
└── README.md
```

---

## Roadmap — Refatoração futura

Quando o projeto crescer, a separação por responsabilidade seguirá o padrão **Flask com Blueprints**:

```
crm_castanheira/
├── app.py                  # Factory create_app() apenas
├── config.py               # Configurações por ambiente (dev/prod)
├── extensions.py           # db, login_manager, etc.
├── models/
│   ├── cliente.py
│   ├── processo.py
│   ├── publicacao.py
│   ├── prazo.py
│   └── tarefa.py
├── routes/                 # Um Blueprint por módulo
│   ├── dashboard.py
│   ├── clientes.py
│   ├── processos.py
│   ├── publicacoes.py
│   ├── prazos.py
│   ├── tarefas.py
│   └── api.py
├── services/               # Lógica de negócio desacoplada das rotas
│   ├── pje_importer.py     # Integração com API PJe
│   └── ia_service.py       # Chamadas ao Claude
└── templates/
```

**Benefícios da separação:**
- Cada módulo testável de forma isolada
- Autenticação (Flask-Login) aplicada por Blueprint
- `services/` reutilizável por CLI, tarefas agendadas ou API REST futura
- Separação clara entre modelo de dados e regra de negócio

---

*v1.1 — Abril/2026*
