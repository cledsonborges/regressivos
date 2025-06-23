#!/usr/bin/env python3
"""
Script de Configuração Completa da Infraestrutura AWS - Ion Regressivos
Autor: Cledson Alves
Data: Junho 2025

Este script configura toda a infraestrutura necessária na AWS:
- DynamoDB Tables
- Lambda Functions
- API Gateway
- S3 Bucket para frontend
- IAM Roles e Policies
"""

import boto3
import json
import time
import zipfile
import os
import sys
from botocore.exceptions import ClientError

class AWSInfrastructureSetup:
    def __init__(self, region='us-east-1'):
        self.region = region
        self.dynamodb = boto3.client('dynamodb', region_name=region)
        self.lambda_client = boto3.client('lambda', region_name=region)
        self.apigateway = boto3.client('apigateway', region_name=region)
        self.s3 = boto3.client('s3', region_name=region)
        self.iam = boto3.client('iam', region_name=region)
        
        # Configurações
        self.project_name = 'ion-regressivos'
        self.bucket_name = f'{self.project_name}-frontend-{int(time.time())}'
        
    def print_step(self, step, message):
        print(f"\n{'='*60}")
        print(f"PASSO {step}: {message}")
        print(f"{'='*60}")
    
    def create_iam_role(self):
        """Cria role IAM para as Lambda functions"""
        self.print_step(1, "Criando IAM Role para Lambda")
        
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "lambda.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        try:
            response = self.iam.create_role(
                RoleName=f'{self.project_name}-lambda-role',
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description='Role para Lambda functions do Ion Regressivos'
            )
            role_arn = response['Role']['Arn']
            print(f"✅ Role criada: {role_arn}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'EntityAlreadyExists':
                response = self.iam.get_role(RoleName=f'{self.project_name}-lambda-role')
                role_arn = response['Role']['Arn']
                print(f"✅ Role já existe: {role_arn}")
            else:
                raise e
        
        # Anexar policies necessárias
        policies = [
            'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
            'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess'
        ]
        
        for policy_arn in policies:
            try:
                self.iam.attach_role_policy(
                    RoleName=f'{self.project_name}-lambda-role',
                    PolicyArn=policy_arn
                )
                print(f"✅ Policy anexada: {policy_arn}")
            except ClientError as e:
                if e.response['Error']['Code'] != 'EntityAlreadyExists':
                    print(f"⚠️ Erro ao anexar policy {policy_arn}: {e}")
        
        # Aguardar propagação da role
        print("⏳ Aguardando propagação da IAM Role...")
        time.sleep(10)
        
        return role_arn
    
    def create_dynamodb_tables(self):
        """Cria as tabelas DynamoDB"""
        self.print_step(2, "Criando Tabelas DynamoDB")
        
        tables_config = [
            {
                'TableName': 'Regressivos',
                'KeySchema': [
                    {'AttributeName': 'regressivoId', 'KeyType': 'HASH'}
                ],
                'AttributeDefinitions': [
                    {'AttributeName': 'regressivoId', 'AttributeType': 'S'}
                ],
                'BillingMode': 'PAY_PER_REQUEST'
            },
            {
                'TableName': 'SquadsModulos',
                'KeySchema': [
                    {'AttributeName': 'squadModuloId', 'KeyType': 'HASH'}
                ],
                'AttributeDefinitions': [
                    {'AttributeName': 'squadModuloId', 'AttributeType': 'S'},
                    {'AttributeName': 'regressivoId', 'AttributeType': 'S'}
                ],
                'GlobalSecondaryIndexes': [
                    {
                        'IndexName': 'RegressivoIdIndex',
                        'KeySchema': [
                            {'AttributeName': 'regressivoId', 'KeyType': 'HASH'}
                        ],
                        'Projection': {'ProjectionType': 'ALL'}
                    }
                ],
                'BillingMode': 'PAY_PER_REQUEST'
            },
            {
                'TableName': 'Configuracoes',
                'KeySchema': [
                    {'AttributeName': 'configuracaoId', 'KeyType': 'HASH'}
                ],
                'AttributeDefinitions': [
                    {'AttributeName': 'configuracaoId', 'AttributeType': 'S'}
                ],
                'BillingMode': 'PAY_PER_REQUEST'
            }
        ]
        
        for table_config in tables_config:
            table_name = table_config['TableName']
            try:
                self.dynamodb.create_table(**table_config)
                print(f"✅ Tabela '{table_name}' criada com sucesso")
                
                # Aguardar tabela ficar ativa
                waiter = self.dynamodb.get_waiter('table_exists')
                waiter.wait(TableName=table_name)
                print(f"✅ Tabela '{table_name}' está ativa")
                
            except ClientError as e:
                if e.response['Error']['Code'] == 'ResourceInUseException':
                    print(f"✅ Tabela '{table_name}' já existe")
                else:
                    print(f"❌ Erro ao criar tabela '{table_name}': {e}")
                    raise e
    
    def load_initial_data(self):
        """Carrega dados iniciais nas tabelas"""
        self.print_step(3, "Carregando Dados Iniciais")
        
        # Dados das squads
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
                    "modules": ["ionCorretoraAcompanhamento", "ionCorretoraCommons", "ionAcompanhamentoPosicaoRendaVariavel", "CorretoraAcompanhamento", "CorretoraCommons", "CorretoraVitrine"]
                },
                {
                    "id": 3,
                    "squad": "03 - TRANSACIONAL DE RENDA VARIÁVEL",
                    "modules": ["ionCorretoraTransacional", "CorretoraTransacional"]
                },
                {
                    "id": 4,
                    "squad": "04 - SQUAD FOUNDATION",
                    "modules": ["ionApp"]
                },
                {
                    "id": 5,
                    "squad": "05 - SQUAD CONTEÚDO E HUMANIZAÇÃO",
                    "modules": ["ionNotificationCentral", "ionCommunications", "ionCentralCampaign", "Conteúdo", "CentraldeNotificacoes"]
                },
                {
                    "id": 6,
                    "squad": "06 - SQUAD CONTRAT E RESGATE DE FUNDOS CANAIS PF",
                    "modules": ["ionContratacaoResgate"]
                },
                {
                    "id": 7,
                    "squad": "07 - ACOMPAN. CANAIS INVESTIMENTOS PF",
                    "modules": ["ionAcompanhamento", "ionHome", "FeatureAcompanhamento"]
                },
                {
                    "id": 8,
                    "squad": "08 - SQUAD VITRINE RF FUNDOS E PREV",
                    "modules": ["ionVitrine", "ionInvestimentosUi"]
                },
                {
                    "id": 9,
                    "squad": "09 - SQUAD VITRINE RV COE",
                    "modules": ["ionVitrine", "ionInvestimentosUi", "FeatureVitrineComparação"]
                },
                {
                    "id": 10,
                    "squad": "10 - SQUAD AGREGADOR",
                    "modules": ["ionAgregador"]
                }
            ]
        }
        
        try:
            self.dynamodb.put_item(
                TableName='Configuracoes',
                Item={
                    'configuracaoId': {'S': 'squads_e_modulos'},
                    'data': {'S': json.dumps(squads_data)}
                }
            )
            print("✅ Dados de squads carregados com sucesso")
        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
    
    def create_lambda_functions(self, role_arn):
        """Cria as Lambda functions"""
        self.print_step(4, "Criando Lambda Functions")
        
        # Código base da Lambda
        lambda_code = '''
import json
import boto3
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
import qrcode
import io
import base64

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    try:
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        path_parameters = event.get('pathParameters') or {}
        query_parameters = event.get('queryStringParameters') or {}
        body = event.get('body', '{}')
        
        if body:
            try:
                body = json.loads(body)
            except:
                body = {}
        
        # Roteamento baseado no path e método
        if path.startswith('/api/admin/'):
            return handle_admin_routes(http_method, path, path_parameters, query_parameters, body)
        elif path.startswith('/api/quality/'):
            return handle_quality_routes(http_method, path, path_parameters, query_parameters, body)
        else:
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                },
                'body': json.dumps({'error': 'Endpoint não encontrado'})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }

def handle_admin_routes(method, path, path_params, query_params, body):
    # Implementar rotas administrativas
    if path == '/api/admin/regressivos' and method == 'GET':
        return list_regressivos()
    elif path == '/api/admin/regressivos' and method == 'POST':
        return create_regressivo(body)
    elif path == '/api/admin/squads-config' and method == 'GET':
        return get_squads_config()
    else:
        return {
            'statusCode': 404,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Rota admin não encontrada'})
        }

def handle_quality_routes(method, path, path_params, query_params, body):
    # Implementar rotas de qualidade
    if path == '/api/quality/regressivos' and method == 'GET':
        return list_active_regressivos()
    else:
        return {
            'statusCode': 404,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Rota quality não encontrada'})
        }

def list_regressivos():
    table = dynamodb.Table('Regressivos')
    response = table.scan()
    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({
            'success': True,
            'data': response.get('Items', [])
        }, default=decimal_default)
    }

def create_regressivo(data):
    table = dynamodb.Table('Regressivos')
    
    regressivo_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    item = {
        'regressivoId': regressivo_id,
        'release': data.get('release'),
        'plataforma': data.get('plataforma'),
        'statusGeral': 'ativo',
        'liberadoEm': now,
        'versaoHomolog': data.get('versaoHomolog'),
        'versaoFirebase': data.get('versaoFirebase'),
        'versaoAlpha': data.get('versaoAlpha'),
        'linkPlanoTestes': data.get('linkPlanoTestes'),
        'tipoRelease': data.get('tipoRelease', 'Normal'),
        'criadoEm': now
    }
    
    table.put_item(Item=item)
    
    return {
        'statusCode': 201,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({
            'success': True,
            'data': item
        }, default=decimal_default)
    }

def get_squads_config():
    table = dynamodb.Table('Configuracoes')
    response = table.get_item(Key={'configuracaoId': 'squads_e_modulos'})
    
    if 'Item' in response:
        data = json.loads(response['Item']['data'])
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'success': True,
                'data': data['squads']
            })
        }
    else:
        return {
            'statusCode': 404,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Configuração não encontrada'})
        }

def list_active_regressivos():
    table = dynamodb.Table('Regressivos')
    response = table.scan(
        FilterExpression='statusGeral = :status',
        ExpressionAttributeValues={':status': 'ativo'}
    )
    
    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({
            'success': True,
            'data': response.get('Items', [])
        }, default=decimal_default)
    }
'''
        
        # Criar arquivo ZIP com o código
        zip_path = '/tmp/lambda_function.zip'
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            zip_file.writestr('lambda_function.py', lambda_code)
        
        # Ler o arquivo ZIP
        with open(zip_path, 'rb') as zip_file:
            zip_content = zip_file.read()
        
        # Criar a Lambda function
        function_name = f'{self.project_name}-api'
        
        try:
            response = self.lambda_client.create_function(
                FunctionName=function_name,
                Runtime='python3.11',
                Role=role_arn,
                Handler='lambda_function.lambda_handler',
                Code={'ZipFile': zip_content},
                Description='API Lambda para Ion Regressivos',
                Timeout=30,
                MemorySize=256,
                Environment={
                    'Variables': {
                        'REGION': self.region
                    }
                }
            )
            print(f"✅ Lambda function '{function_name}' criada com sucesso")
            return response['FunctionArn']
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceConflictException':
                print(f"✅ Lambda function '{function_name}' já existe")
                response = self.lambda_client.get_function(FunctionName=function_name)
                return response['Configuration']['FunctionArn']
            else:
                print(f"❌ Erro ao criar Lambda function: {e}")
                raise e
    
    def create_api_gateway(self, lambda_arn):
        """Cria API Gateway"""
        self.print_step(5, "Criando API Gateway")
        
        # Criar REST API
        api_name = f'{self.project_name}-api'
        
        try:
            response = self.apigateway.create_rest_api(
                name=api_name,
                description='API Gateway para Ion Regressivos',
                endpointConfiguration={
                    'types': ['REGIONAL']
                }
            )
            api_id = response['id']
            print(f"✅ API Gateway criada: {api_id}")
        except Exception as e:
            print(f"❌ Erro ao criar API Gateway: {e}")
            return None
        
        # Obter root resource
        resources = self.apigateway.get_resources(restApiId=api_id)
        root_resource_id = None
        for resource in resources['items']:
            if resource['path'] == '/':
                root_resource_id = resource['id']
                break
        
        # Criar recurso proxy
        try:
            proxy_resource = self.apigateway.create_resource(
                restApiId=api_id,
                parentId=root_resource_id,
                pathPart='{proxy+}'
            )
            proxy_resource_id = proxy_resource['id']
            print(f"✅ Recurso proxy criado: {proxy_resource_id}")
        except Exception as e:
            print(f"❌ Erro ao criar recurso proxy: {e}")
            return None
        
        # Criar método ANY
        try:
            self.apigateway.put_method(
                restApiId=api_id,
                resourceId=proxy_resource_id,
                httpMethod='ANY',
                authorizationType='NONE'
            )
            print("✅ Método ANY criado")
        except Exception as e:
            print(f"❌ Erro ao criar método: {e}")
        
        # Configurar integração com Lambda
        lambda_uri = f"arn:aws:apigateway:{self.region}:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
        
        try:
            self.apigateway.put_integration(
                restApiId=api_id,
                resourceId=proxy_resource_id,
                httpMethod='ANY',
                type='AWS_PROXY',
                integrationHttpMethod='POST',
                uri=lambda_uri
            )
            print("✅ Integração com Lambda configurada")
        except Exception as e:
            print(f"❌ Erro ao configurar integração: {e}")
        
        # Dar permissão para API Gateway invocar Lambda
        try:
            function_name = lambda_arn.split(':')[-1]
            self.lambda_client.add_permission(
                FunctionName=function_name,
                StatementId='api-gateway-invoke',
                Action='lambda:InvokeFunction',
                Principal='apigateway.amazonaws.com',
                SourceArn=f"arn:aws:execute-api:{self.region}:*:{api_id}/*/*"
            )
            print("✅ Permissão para API Gateway configurada")
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceConflictException':
                print(f"⚠️ Erro ao configurar permissão: {e}")
        
        # Deploy da API
        try:
            self.apigateway.create_deployment(
                restApiId=api_id,
                stageName='prod'
            )
            print("✅ API deployada em produção")
        except Exception as e:
            print(f"❌ Erro ao fazer deploy: {e}")
        
        api_url = f"https://{api_id}.execute-api.{self.region}.amazonaws.com/prod"
        print(f"🌐 URL da API: {api_url}")
        
        return api_url
    
    def create_s3_bucket(self):
        """Cria bucket S3 para frontend"""
        self.print_step(6, "Criando Bucket S3 para Frontend")
        
        try:
            if self.region == 'us-east-1':
                self.s3.create_bucket(Bucket=self.bucket_name)
            else:
                self.s3.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
            print(f"✅ Bucket S3 criado: {self.bucket_name}")
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyExists':
                print(f"✅ Bucket S3 já existe: {self.bucket_name}")
            else:
                print(f"❌ Erro ao criar bucket: {e}")
                raise e
        
        # Configurar website hosting
        try:
            self.s3.put_bucket_website(
                Bucket=self.bucket_name,
                WebsiteConfiguration={
                    'IndexDocument': {'Suffix': 'index.html'},
                    'ErrorDocument': {'Key': 'index.html'}
                }
            )
            print("✅ Website hosting configurado")
        except Exception as e:
            print(f"❌ Erro ao configurar website: {e}")
        
        # Configurar política pública
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{self.bucket_name}/*"
                }
            ]
        }
        
        try:
            self.s3.put_bucket_policy(
                Bucket=self.bucket_name,
                Policy=json.dumps(bucket_policy)
            )
            print("✅ Política pública configurada")
        except Exception as e:
            print(f"❌ Erro ao configurar política: {e}")
        
        website_url = f"http://{self.bucket_name}.s3-website.{self.region}.amazonaws.com"
        print(f"🌐 URL do Website: {website_url}")
        
        return self.bucket_name, website_url
    
    def run_setup(self):
        """Executa todo o setup da infraestrutura"""
        print("🚀 Iniciando configuração da infraestrutura AWS para Ion Regressivos")
        print(f"📍 Região: {self.region}")
        
        try:
            # 1. Criar IAM Role
            role_arn = self.create_iam_role()
            
            # 2. Criar tabelas DynamoDB
            self.create_dynamodb_tables()
            
            # 3. Carregar dados iniciais
            self.load_initial_data()
            
            # 4. Criar Lambda functions
            lambda_arn = self.create_lambda_functions(role_arn)
            
            # 5. Criar API Gateway
            api_url = self.create_api_gateway(lambda_arn)
            
            # 6. Criar bucket S3
            bucket_name, website_url = self.create_s3_bucket()
            
            # Resumo final
            print(f"\n{'='*60}")
            print("🎉 INFRAESTRUTURA CRIADA COM SUCESSO!")
            print(f"{'='*60}")
            print(f"🗄️ Tabelas DynamoDB: Regressivos, SquadsModulos, Configuracoes")
            print(f"⚡ Lambda Function: {lambda_arn}")
            print(f"🌐 API Gateway: {api_url}")
            print(f"📦 S3 Bucket: {bucket_name}")
            print(f"🌍 Website URL: {website_url}")
            print(f"{'='*60}")
            
            # Salvar configurações
            config = {
                'region': self.region,
                'lambda_arn': lambda_arn,
                'api_url': api_url,
                'bucket_name': bucket_name,
                'website_url': website_url
            }
            
            with open('aws_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            print("✅ Configurações salvas em aws_config.json")
            
            return config
            
        except Exception as e:
            print(f"\n❌ ERRO DURANTE A CONFIGURAÇÃO: {e}")
            sys.exit(1)

def main():
    if len(sys.argv) > 1:
        region = sys.argv[1]
    else:
        region = 'us-east-1'
    
    setup = AWSInfrastructureSetup(region)
    setup.run_setup()

if __name__ == '__main__':
    main()

