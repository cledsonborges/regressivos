# Ion Regressivos - Sistema de Gerenciamento de Testes Regressivos

**Autor:** Cledson Alves  
**Empresa:** Ion Investimentos  
**Data:** Junho 2025  

## Visão Geral

O Ion Regressivos é uma aplicação completa para gerenciamento de testes regressivos, desenvolvida especificamente para o time de qualidade da Ion Investimentos. O sistema oferece um painel administrativo para criação e gestão de regressivos, além de uma interface dedicada para o time de qualidade atualizar status dos testes.

## Características Principais

### 🎯 Funcionalidades Core
- **Painel Administrativo**: Criação, edição e exclusão de regressivos
- **Dashboard de Qualidade**: Interface para atualização de status dos testes
- **SLA Automático**: Controle de tempo com regra de 24 horas
- **Geração de Release Notes**: Integração com IA Gemini para geração automática
- **QR Codes**: Geração automática para versões Homolog e Alpha
- **Gestão de Squads**: CRUD completo para squads e módulos

### 🔧 Tecnologias Utilizadas
- **Frontend**: React 18 + Vite + Tailwind CSS + shadcn/ui
- **Backend**: Flask + Python 3.11
- **Banco de Dados**: AWS DynamoDB
- **Infraestrutura**: AWS (DynamoDB, S3, IAM)
- **IA**: Google Gemini API para release notes
- **Versionamento**: Git + GitHub

### 🎨 Design System
- **Cores Primárias**: 
  - Ion Dark: `#133134`
  - Ion Green: `#A7CE2E`
- **Tipografia**: Sistema responsivo com Tailwind CSS
- **Componentes**: shadcn/ui para consistência visual

## Arquitetura do Sistema

### Estrutura de Pastas
```
regressivos/
├── backend/
│   └── regressivos_backend/
│       ├── src/
│       │   ├── models/          # Modelos de dados
│       │   ├── routes/          # Rotas da API
│       │   └── main.py          # Aplicação principal
│       ├── venv/                # Ambiente virtual Python
│       └── requirements.txt     # Dependências Python
├── frontend/
│   └── regressivos_frontend/
│       ├── src/
│       │   ├── components/      # Componentes React
│       │   ├── assets/          # Assets estáticos
│       │   └── App.jsx          # Aplicação principal
│       ├── public/              # Arquivos públicos
│       └── package.json         # Dependências Node.js
├── aws_structure.md             # Documentação da infraestrutura AWS
├── create_dynamodb_tables.py    # Script de criação das tabelas
├── upload_squads_data.py        # Script de carga inicial
└── README.md                    # Esta documentação
```

### Banco de Dados (DynamoDB)

#### Tabela: Regressivos
- **Primary Key**: `regressivoId` (String, UUID)
- **Atributos**:
  - `release`: Identificação da release (ex: R113)
  - `ambiente`: Ambiente de teste
  - `statusGeral`: Status do regressivo (ativo/finalizado)
  - `slaInicio/slaFim`: Controle de SLA
  - `versaoHomolog/versaoAlpha/versaoFirebase`: Versões
  - `linkPlanoTestes`: URL do plano de testes
  - `qrCodeHomolog/qrCodeAlpha`: QR codes em base64
  - `tipoRelease`: Normal ou Exclusiva
  - `plataforma`: Android ou iOS

#### Tabela: SquadsModulos
- **Primary Key**: `squadModuloId` (String, UUID)
- **GSI**: `RegressivoIdIndex` para consultas por regressivo
- **Atributos**:
  - `squad`: Nome da squad
  - `modulo`: Módulo específico
  - `detalheEntrega`: Descrição da entrega
  - `responsavel`: Responsável pelo teste
  - `status`: concluído, em andamento, bloqueado, concluído com bugs
  - `reportarBug`: Descrição de bugs encontrados
  - `regressivoId`: Referência ao regressivo

#### Tabela: Configuracoes
- **Primary Key**: `configuracaoId` (String)
- **Atributos**:
  - `data`: JSON com configurações (squads e módulos)

## APIs Disponíveis

### Endpoints Administrativos (`/api/admin/`)
- `GET /regressivos` - Lista todos os regressivos
- `POST /regressivos` - Cria novo regressivo
- `GET /regressivos/{id}` - Busca regressivo específico
- `PUT /regressivos/{id}` - Atualiza regressivo
- `DELETE /regressivos/{id}` - Exclui regressivo
- `POST /regressivos/{id}/iniciar-sla` - Inicia SLA
- `POST /regressivos/{id}/parar-sla` - Para SLA
- `POST /regressivos/{id}/incluir-tempo` - Adiciona tempo ao SLA
- `POST /regressivos/{id}/release-notes` - Gera release notes
- `GET /squads-config` - Busca configuração de squads
- `PUT /squads-config` - Atualiza configuração de squads

### Endpoints de Qualidade (`/api/quality/`)
- `GET /regressivos` - Lista regressivos ativos
- `GET /regressivos/{id}` - Detalhes completos do regressivo
- `PUT /squad-modulo/{id}` - Atualiza status de squad/módulo
- `GET /squad-modulo/{id}` - Busca squad/módulo específico
- `GET /regressivos/{id}/status-resumo` - Resumo de progresso
- `GET /regressivos/{id}/verificar-sla` - Status do SLA

## Instalação e Configuração

### Pré-requisitos
- Python 3.11+
- Node.js 20+
- Conta AWS com credenciais configuradas
- Chave da API Gemini

### Configuração do Backend

1. **Instalar dependências**:
```bash
cd backend/regressivos_backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

2. **Configurar AWS**:
```bash
# Configurar credenciais AWS
aws configure
# ou criar ~/.aws/credentials
```

3. **Criar tabelas DynamoDB**:
```bash
python create_dynamodb_tables.py
python upload_squads_data.py
```

4. **Iniciar servidor**:
```bash
python src/main.py
```

### Configuração do Frontend

1. **Instalar dependências**:
```bash
cd frontend/regressivos_frontend
pnpm install
```

2. **Iniciar desenvolvimento**:
```bash
pnpm run dev --host
```

3. **Build para produção**:
```bash
pnpm run build
```

## Funcionalidades Detalhadas

### Sistema de SLA
- **Duração**: 24 horas após início
- **Controles**: Iniciar, parar, incluir tempo adicional
- **Bloqueio**: Edições bloqueadas após vencimento
- **Alertas**: Contador regressivo em tempo real

### Gestão de Status
- **Concluído**: Teste finalizado com sucesso
- **Em Andamento**: Teste em execução
- **Bloqueado**: Teste impedido por dependências
- **Concluído com Bugs**: Teste finalizado com problemas

### Geração de Release Notes
- **IA Integrada**: Utiliza Google Gemini API
- **Contexto Automático**: Baseado nas entregas das squads
- **Formato Profissional**: Estrutura padronizada
- **Edição**: Possibilidade de editar antes de usar

### QR Codes
- **Geração Automática**: Para versões Homolog e Alpha
- **Formato**: Base64 incorporado na resposta
- **Uso**: Facilita acesso às versões de teste

## Segurança e Boas Práticas

### Autenticação
- Sistema de login simples por perfil
- Controle de acesso baseado em roles (admin/quality)
- Sessão persistente no localStorage

### Validações
- Validação de SLA antes de edições
- Verificação de permissões por endpoint
- Sanitização de inputs

### Performance
- Lazy loading de componentes React
- Otimização de consultas DynamoDB
- Cache de configurações

## Deploy e Produção

### Backend (Flask)
```bash
# Usando o utilitário de deploy
service_deploy_backend flask backend/regressivos_backend
```

### Frontend (React)
```bash
# Build e deploy
cd frontend/regressivos_frontend
pnpm run build
service_deploy_frontend static dist/
```

### Infraestrutura AWS
- **DynamoDB**: Tabelas configuradas em us-east-1
- **IAM**: Permissões mínimas necessárias
- **S3**: Hosting do frontend (opcional)

## Migração de Conta AWS

Para migrar para uma nova conta AWS, execute:

```bash
# 1. Configurar novas credenciais
aws configure

# 2. Recriar infraestrutura
python create_dynamodb_tables.py
python upload_squads_data.py

# 3. Atualizar configurações no código se necessário
```

## Monitoramento e Logs

### Logs do Backend
- Logs automáticos do Flask em modo debug
- Tratamento de erros com mensagens descritivas
- Logs de operações DynamoDB

### Métricas Importantes
- Tempo de resposta das APIs
- Taxa de sucesso/erro das operações
- Utilização das tabelas DynamoDB

## Troubleshooting

### Problemas Comuns

**Backend não inicia**:
- Verificar credenciais AWS
- Confirmar instalação das dependências
- Verificar se a porta 5000 está livre

**Frontend não carrega**:
- Verificar se o backend está rodando
- Confirmar instalação do pnpm/npm
- Verificar se a porta 5173 está livre

**Erro de conexão DynamoDB**:
- Verificar credenciais AWS
- Confirmar região (us-east-1)
- Verificar se as tabelas existem

**SLA não funciona**:
- Verificar formato das datas
- Confirmar timezone do servidor
- Verificar se o SLA foi iniciado

## Contribuição

### Padrões de Código
- **Python**: PEP 8
- **JavaScript**: ESLint + Prettier
- **Git**: Conventional Commits

### Estrutura de Commits
```
feat: adiciona nova funcionalidade
fix: corrige bug específico
docs: atualiza documentação
style: ajustes de formatação
refactor: refatoração de código
test: adiciona ou corrige testes
```

## Suporte

Para suporte técnico ou dúvidas sobre o sistema:

- **Desenvolvedor**: Cledson Alves
- **Repositório**: https://github.com/cledsonborges/regressivos
- **Documentação**: Este README.md

## Licença

Este projeto é propriedade da Ion Investimentos e destina-se exclusivamente ao uso interno da empresa.

---

**Desenvolvido com ❤️ para Ion Investimentos**  
*Sistema Ion Regressivos v1.0 - 2025*

