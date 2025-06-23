import boto3

def create_dynamodb_tables():
    dynamodb = boto3.client('dynamodb', region_name='us-east-1') # Usando us-east-1 como região padrão

    # Tabela Regressivos
    try:
        dynamodb.create_table(
            TableName='Regressivos',
            KeySchema=[
                {
                    'AttributeName': 'regressivoId',
                    'KeyType': 'HASH'  # Partition key
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
        print("Tabela 'Regressivos' criada com sucesso.")
    except Exception as e:
        print(f"Erro ao criar a tabela 'Regressivos': {e}")

    # Tabela SquadsModulos
    try:
        dynamodb.create_table(
            TableName='SquadsModulos',
            KeySchema=[
                {
                    'AttributeName': 'squadModuloId',
                    'KeyType': 'HASH'  # Partition key
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
        print("Tabela 'SquadsModulos' criada com sucesso.")
    except Exception as e:
        print(f"Erro ao criar a tabela 'SquadsModulos': {e}")

    # Tabela Configuracoes
    try:
        dynamodb.create_table(
            TableName='Configuracoes',
            KeySchema=[
                {
                    'AttributeName': 'configuracaoId',
                    'KeyType': 'HASH'  # Partition key
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
        print("Tabela 'Configuracoes' criada com sucesso.")
    except Exception as e:
        print(f"Erro ao criar a tabela 'Configuracoes': {e}")

if __name__ == '__main__':
    create_dynamodb_tables()


