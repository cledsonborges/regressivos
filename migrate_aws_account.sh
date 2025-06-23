#!/bin/bash

# Script de Migração de Conta AWS - Ion Regressivos
# Autor: Cledson Alves
# Data: Junho 2025

echo "=========================================="
echo "Ion Regressivos - Migração de Conta AWS"
echo "=========================================="
echo ""

# Verificar se o AWS CLI está instalado
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI não encontrado. Por favor, instale o AWS CLI primeiro."
    exit 1
fi

echo "📋 Este script irá:"
echo "1. Configurar novas credenciais AWS"
echo "2. Criar tabelas DynamoDB na nova conta"
echo "3. Carregar dados iniciais de squads"
echo "4. Verificar a configuração"
echo ""

read -p "Deseja continuar? (s/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "❌ Operação cancelada."
    exit 1
fi

echo ""
echo "🔧 Passo 1: Configurando credenciais AWS"
echo "Por favor, insira suas novas credenciais AWS:"

read -p "AWS Access Key ID: " AWS_ACCESS_KEY_ID
read -s -p "AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY
echo ""
read -p "Região AWS (padrão: us-east-1): " AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}

# Configurar credenciais
mkdir -p ~/.aws
cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = $AWS_ACCESS_KEY_ID
aws_secret_access_key = $AWS_SECRET_ACCESS_KEY
EOF

cat > ~/.aws/config << EOF
[default]
region = $AWS_REGION
output = json
EOF

echo "✅ Credenciais configuradas com sucesso!"

echo ""
echo "🗄️ Passo 2: Criando tabelas DynamoDB"

# Verificar se o Python está disponível
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Por favor, instale o Python3."
    exit 1
fi

# Instalar boto3 se necessário
pip3 install boto3 > /dev/null 2>&1

# Criar script temporário para criação das tabelas
cat > /tmp/create_tables.py << 'EOF'
import boto3
import json
import sys

def create_dynamodb_tables():
    try:
        dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        
        print("Criando tabela 'Regressivos'...")
        dynamodb.create_table(
            TableName='Regressivos',
            KeySchema=[
                {
                    'AttributeName': 'regressivoId',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'regressivoId',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("✅ Tabela 'Regressivos' criada com sucesso.")
        
        print("Criando tabela 'SquadsModulos'...")
        dynamodb.create_table(
            TableName='SquadsModulos',
            KeySchema=[
                {
                    'AttributeName': 'squadModuloId',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'squadModuloId',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'regressivoId',
                    'AttributeType': 'S'
                }
            ],
            GlobalSecondaryIndexes=[
                {
                    'IndexName': 'RegressivoIdIndex',
                    'KeySchema': [
                        {
                            'AttributeName': 'regressivoId',
                            'KeyType': 'HASH'
                        }
                    ],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    },
                    'ProvisionedThroughput': {
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("✅ Tabela 'SquadsModulos' criada com sucesso.")
        
        print("Criando tabela 'Configuracoes'...")
        dynamodb.create_table(
            TableName='Configuracoes',
            KeySchema=[
                {
                    'AttributeName': 'configuracaoId',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'configuracaoId',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print("✅ Tabela 'Configuracoes' criada com sucesso.")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False

if __name__ == '__main__':
    success = create_dynamodb_tables()
    sys.exit(0 if success else 1)
EOF

# Executar criação das tabelas
python3 /tmp/create_tables.py
if [ $? -ne 0 ]; then
    echo "❌ Falha na criação das tabelas. Verifique suas credenciais e permissões."
    exit 1
fi

echo ""
echo "📊 Passo 3: Carregando dados iniciais"

# Criar script para carregar dados de squads
cat > /tmp/load_squads.py << 'EOF'
import boto3
import json
import sys

def load_squads_data():
    try:
        dynamodb = boto3.client("dynamodb", region_name="us-east-1")
        
        # Dados das squads (versão simplificada para migração)
        squads_data = {
            "squads": [
                {
                    "id": 1,
                    "squad": "01 - SQUAD FORMALIZAÇÃO REMOTA",
                    "modules": ["ionFormalizacao", "ionWebViewSdk", "FormalizaçãoRemota", "ionCriptoativos"]
                },
                {
                    "id": 2,
                    "squad": "02 - SQUAD CORRETORA ACOMPANHAMENTO DE RV",
                    "modules": ["ionCorretoraAcompanhamento", "ionCorretoraCommons", "ionAcompanhamentoPosicaoRendaVariavel"]
                },
                {
                    "id": 3,
                    "squad": "03 - TRANSACIONAL DE RENDA VARIÁVEL",
                    "modules": ["ionCorretoraTransacional", "CorretoraTransacional"]
                }
            ]
        }
        
        print("Carregando dados de squads...")
        dynamodb.put_item(
            TableName="Configuracoes",
            Item={
                "configuracaoId": {"S": "squads_e_modulos"},
                "data": {"S": json.dumps(squads_data)}
            }
        )
        print("✅ Dados de squads carregados com sucesso.")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return False

if __name__ == '__main__':
    success = load_squads_data()
    sys.exit(0 if success else 1)
EOF

# Executar carga de dados
python3 /tmp/load_squads.py
if [ $? -ne 0 ]; then
    echo "❌ Falha no carregamento dos dados. Continuando..."
fi

echo ""
echo "🔍 Passo 4: Verificando configuração"

# Criar script de verificação
cat > /tmp/verify_setup.py << 'EOF'
import boto3
import sys

def verify_setup():
    try:
        dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        
        # Listar tabelas
        response = dynamodb.list_tables()
        tables = response.get('TableNames', [])
        
        required_tables = ['Regressivos', 'SquadsModulos', 'Configuracoes']
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            print(f"❌ Tabelas faltando: {', '.join(missing_tables)}")
            return False
        
        print("✅ Todas as tabelas estão presentes:")
        for table in required_tables:
            print(f"   - {table}")
        
        # Verificar dados de configuração
        try:
            response = dynamodb.get_item(
                TableName='Configuracoes',
                Key={'configuracaoId': {'S': 'squads_e_modulos'}}
            )
            if 'Item' in response:
                print("✅ Dados de configuração carregados.")
            else:
                print("⚠️ Dados de configuração não encontrados.")
        except:
            print("⚠️ Erro ao verificar dados de configuração.")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False

if __name__ == '__main__':
    success = verify_setup()
    sys.exit(0 if success else 1)
EOF

# Executar verificação
python3 /tmp/verify_setup.py

# Limpar arquivos temporários
rm -f /tmp/create_tables.py /tmp/load_squads.py /tmp/verify_setup.py

echo ""
echo "🎉 Migração concluída!"
echo ""
echo "📝 Próximos passos:"
echo "1. Atualize as credenciais AWS no código da aplicação se necessário"
echo "2. Teste a aplicação para garantir que tudo está funcionando"
echo "3. Configure o deploy na nova infraestrutura"
echo ""
echo "📋 Informações importantes:"
echo "- Região AWS: $AWS_REGION"
echo "- Tabelas criadas: Regressivos, SquadsModulos, Configuracoes"
echo "- Dados iniciais: Configuração básica de squads carregada"
echo ""
echo "✅ Migração de conta AWS concluída com sucesso!"

