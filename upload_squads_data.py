import boto3
import json

def upload_squads_data(file_path):
    dynamodb = boto3.client("dynamodb", region_name="us-east-1")

    with open(file_path, "r") as f:
        squads_data = json.load(f)

    try:
        dynamodb.put_item(
            TableName="Configuracoes",
            Item={
                "configuracaoId": {"S": "squads_e_modulos"},
                "data": {"S": json.dumps(squads_data)}
            }
        )
        print("Dados de squads e módulos carregados com sucesso para a tabela Configuracoes.")
    except Exception as e:
        print(f"Erro ao carregar dados de squads e módulos: {e}")

if __name__ == "__main__":
    upload_squads_data("/home/ubuntu/upload/squads.json")


