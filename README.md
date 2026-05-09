# Catalog Service

Microserviço responsável pelo cadastro e gestão do ciclo de vida de veículos à venda na plataforma FIAP SUB.

## Visão Geral

| Item | Detalhe |
|------|---------|
| Runtime | Python 3.11+ |
| Framework | FastAPI |
| Banco de dados | MongoDB 7 (Motor + Beanie) |
| Autenticação | OAuth2 Bearer JWT (python-jose) |
| Porta padrão | 8000 |

### Endpoints

| Método | Rota | Descrição | Auth |
|--------|------|-----------|------|
| `POST` | `/vehicles` | Registrar veículo | ✅ |
| `GET` | `/vehicles` | Listar veículos disponíveis (paginado) | ✅ |
| `GET` | `/vehicles/{id}` | Obter veículo por ID | ✅ |
| `PUT` | `/vehicles/{id}` | Atualizar dados do veículo | ✅ |
| `PATCH` | `/vehicles/{id}/status` | Atualizar status (`available` ↔ `sold`) | ✅ |
| `GET` | `/health` | Health check | ❌ |
| `GET` | `/docs` | Documentação OpenAPI interativa | ❌ |

---

## Pré-requisitos

- Python 3.11+
- Docker e Docker Compose
- (Opcional) `sonar-scanner` para análise de qualidade local

---

## Variáveis de Ambiente

Copie `.env.example` para `.env` e ajuste os valores:

```bash
cp .env.example .env
```

| Variável | Descrição | Exemplo |
|----------|-----------|---------|
| `MONGODB_URI` | URI de conexão com o MongoDB | `mongodb://localhost:27017/catalog` |
| `JWT_SECRET_KEY` | Chave secreta para validação de tokens JWT | `sua-chave-secreta` |
| `JWT_ALGORITHM` | Algoritmo de assinatura JWT | `HS256` |

---

## Rodando com Docker Compose (recomendado)

Sobe o catalog-service, MongoDB e SonarQube:

```bash
docker compose up -d
```

Verifica se o serviço está saudável:

```bash
curl http://localhost:8000/health
# {"status": "ok"}
```

Derruba a stack:

```bash
docker compose down
```

---

## Rodando Localmente (desenvolvimento)

### 1. Criar e ativar o ambiente virtual

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 2. Instalar dependências

```bash
pip install -e ".[dev]"
```

### 3. Subir MongoDB

```bash
docker compose up -d mongodb
```

### 4. Configurar variáveis de ambiente

```bash
export MONGODB_URI=mongodb://localhost:27017/catalog
export JWT_SECRET_KEY=dev-secret
export JWT_ALGORITHM=HS256
```

Ou crie um arquivo `.env` e carregue com:

```bash
set -a && source .env && set +a
```

### 5. Iniciar o servidor

```bash
cd src
uvicorn presentation.main:app --reload --host 0.0.0.0 --port 8000
```

Acesse a documentação interativa em: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Testes

### Executar todos os testes com coverage

```bash
cd src
pytest
```

O relatório de cobertura é exibido no terminal. A cobertura mínima exigida é **80%**.

### Executar apenas testes unitários

```bash
pytest tests/unit/
```

### Executar apenas testes de integração (contrato)

```bash
pytest tests/integration/
```

### Gerar relatório XML (usado pelo SonarQube)

```bash
pytest --cov-report=xml:coverage.xml
```

---

## Lint e Formatação

```bash
# Verificar lint
ruff check src/ tests/

# Aplicar correções automáticas
ruff check --fix src/ tests/

# Formatar código
black src/ tests/
```

---

## Análise de Qualidade — SonarQube Local

### 1. Subir SonarQube

```bash
docker compose up -d sonar
```

Aguarde o SonarQube inicializar (pode levar ~1 min) e acesse: [http://localhost:9000](http://localhost:9000)

Credenciais padrão: `admin` / `admin`

### 2. Gerar relatório de cobertura

```bash
cd src
pytest --cov-report=xml:../coverage.xml
```

### 3. Executar análise

```bash
sonar-scanner \
  -Dsonar.login=<seu-token-sonar>
```

O arquivo `sonar-project.properties` na raiz do projeto já está pré-configurado.

---

## Estrutura do Projeto

```
.
├── src/
│   ├── domain/
│   │   ├── entities/          # Entidade Vehicle e VehicleStatus
│   │   └── repositories/      # Interface abstrata VehicleRepository
│   ├── application/
│   │   └── use_cases/         # CreateVehicle, UpdateVehicle, GetVehicle, ListAvailableVehicles, UpdateVehicleStatus
│   ├── infrastructure/
│   │   ├── auth/              # OAuth2 JWT middleware
│   │   └── database/          # Implementação Motor/Beanie + VehicleDocument
│   └── presentation/
│       ├── routers/           # FastAPI routers (vehicles, vehicle_status, health)
│       ├── schemas/           # Schemas Pydantic de request/response
│       └── main.py            # Instância FastAPI e lifespan
├── tests/
│   ├── unit/                  # Testes unitários (domain, application, infrastructure)
│   └── integration/           # Testes de contrato HTTP
├── docs/
│   ├── c4-component.md        # Diagrama C4 de componentes
│   └── sequence-diagrams.md   # Diagramas de sequência
├── Dockerfile                 # Multi-stage build
├── docker-compose.yml         # Stack local: catalog + MongoDB + SonarQube
├── sonar-project.properties   # Configuração SonarQube
└── pyproject.toml             # Dependências e configuração de ferramentas
```

---

## Arquitetura

O serviço segue **Clean Architecture** em quatro camadas:

```
Presentation (FastAPI routers + schemas)
     ↓
Application (use cases — orquestração)
     ↓
Domain (entidades + interfaces de repositório)
     ↑
Infrastructure (MongoDB/Beanie + JWT)
```

Consulte [docs/c4-component.md](docs/c4-component.md) para o diagrama de componentes e [docs/sequence-diagrams.md](docs/sequence-diagrams.md) para os fluxos de sequência.

---

## Pre-commit Hooks

O repositório usa `pre-commit` para validação de mensagens de commit (Conventional Commits):

```bash
pre-commit install
```

Formato esperado: `type(scope): descrição` — ex: `feat(vehicles): add pagination support`

---

## Conventional Commits

| Tipo | Quando usar |
|------|-------------|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `test` | Adição ou correção de testes |
| `refactor` | Refatoração sem mudança de comportamento |
| `docs` | Documentação |
| `chore` | Tarefas de manutenção (deps, config) |
| `ci` | Pipeline CI/CD |
