import boto3
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class RegressivoModel:
    def __init__(self):
        self.dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        self.table_name = 'Regressivos'
    
    def create_regressivo(self, data: Dict) -> Dict:
        """Cria um novo regressivo"""
        regressivo_id = str(uuid.uuid4())
        
        item = {
            'regressivoId': {'S': regressivo_id},
            'release': {'S': data.get('release', '')},
            'ambiente': {'S': data.get('ambiente', '')},
            'statusGeral': {'S': 'ativo'},
            'slaInicio': {'S': ''},
            'slaFim': {'S': ''},
            'liberadoEm': {'S': datetime.now().isoformat()},
            'versaoHomolog': {'S': data.get('versaoHomolog', '')},
            'versaoFirebase': {'S': data.get('versaoFirebase', '')},
            'versaoAlpha': {'S': data.get('versaoAlpha', '')},
            'linkPlanoTestes': {'S': data.get('linkPlanoTestes', '')},
            'qrCodeHomolog': {'S': data.get('qrCodeHomolog', '')},
            'qrCodeAlpha': {'S': data.get('qrCodeAlpha', '')},
            'tipoRelease': {'S': data.get('tipoRelease', 'Normal')},
            'plataforma': {'S': data.get('plataforma', '')}
        }
        
        self.dynamodb.put_item(TableName=self.table_name, Item=item)
        return {'regressivoId': regressivo_id, **data}
    
    def get_regressivo(self, regressivo_id: str) -> Optional[Dict]:
        """Busca um regressivo por ID"""
        try:
            response = self.dynamodb.get_item(
                TableName=self.table_name,
                Key={'regressivoId': {'S': regressivo_id}}
            )
            
            if 'Item' in response:
                return self._deserialize_item(response['Item'])
            return None
        except Exception as e:
            print(f"Erro ao buscar regressivo: {e}")
            return None
    
    def list_regressivos(self) -> List[Dict]:
        """Lista todos os regressivos"""
        try:
            response = self.dynamodb.scan(TableName=self.table_name)
            return [self._deserialize_item(item) for item in response.get('Items', [])]
        except Exception as e:
            print(f"Erro ao listar regressivos: {e}")
            return []
    
    def update_regressivo(self, regressivo_id: str, data: Dict) -> bool:
        """Atualiza um regressivo"""
        try:
            update_expression = "SET "
            expression_attribute_values = {}
            
            for key, value in data.items():
                if key != 'regressivoId':
                    update_expression += f"{key} = :{key}, "
                    expression_attribute_values[f":{key}"] = {'S': str(value)}
            
            update_expression = update_expression.rstrip(', ')
            
            self.dynamodb.update_item(
                TableName=self.table_name,
                Key={'regressivoId': {'S': regressivo_id}},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            return True
        except Exception as e:
            print(f"Erro ao atualizar regressivo: {e}")
            return False
    
    def delete_regressivo(self, regressivo_id: str) -> bool:
        """Exclui um regressivo"""
        try:
            self.dynamodb.delete_item(
                TableName=self.table_name,
                Key={'regressivoId': {'S': regressivo_id}}
            )
            return True
        except Exception as e:
            print(f"Erro ao excluir regressivo: {e}")
            return False
    
    def iniciar_sla(self, regressivo_id: str) -> bool:
        """Inicia o SLA de um regressivo (24 horas)"""
        try:
            sla_inicio = datetime.now()
            sla_fim = sla_inicio + timedelta(hours=24)
            
            self.dynamodb.update_item(
                TableName=self.table_name,
                Key={'regressivoId': {'S': regressivo_id}},
                UpdateExpression="SET slaInicio = :inicio, slaFim = :fim",
                ExpressionAttributeValues={
                    ':inicio': {'S': sla_inicio.isoformat()},
                    ':fim': {'S': sla_fim.isoformat()}
                }
            )
            return True
        except Exception as e:
            print(f"Erro ao iniciar SLA: {e}")
            return False
    
    def parar_sla(self, regressivo_id: str) -> bool:
        """Para o SLA de um regressivo"""
        try:
            self.dynamodb.update_item(
                TableName=self.table_name,
                Key={'regressivoId': {'S': regressivo_id}},
                UpdateExpression="SET statusGeral = :status",
                ExpressionAttributeValues={
                    ':status': {'S': 'finalizado'}
                }
            )
            return True
        except Exception as e:
            print(f"Erro ao parar SLA: {e}")
            return False
    
    def incluir_tempo_sla(self, regressivo_id: str, horas: int) -> bool:
        """Inclui mais tempo no SLA"""
        try:
            regressivo = self.get_regressivo(regressivo_id)
            if not regressivo or not regressivo.get('slaFim'):
                return False
            
            sla_fim_atual = datetime.fromisoformat(regressivo['slaFim'])
            novo_sla_fim = sla_fim_atual + timedelta(hours=horas)
            
            self.dynamodb.update_item(
                TableName=self.table_name,
                Key={'regressivoId': {'S': regressivo_id}},
                UpdateExpression="SET slaFim = :fim",
                ExpressionAttributeValues={
                    ':fim': {'S': novo_sla_fim.isoformat()}
                }
            )
            return True
        except Exception as e:
            print(f"Erro ao incluir tempo no SLA: {e}")
            return False
    
    def verificar_sla_vencido(self, regressivo_id: str) -> bool:
        """Verifica se o SLA de um regressivo venceu"""
        try:
            regressivo = self.get_regressivo(regressivo_id)
            if not regressivo or not regressivo.get('slaFim'):
                return False
            
            sla_fim = datetime.fromisoformat(regressivo['slaFim'])
            return datetime.now() > sla_fim
        except Exception as e:
            print(f"Erro ao verificar SLA: {e}")
            return False
    
    def _deserialize_item(self, item: Dict) -> Dict:
        """Converte item do DynamoDB para formato Python"""
        result = {}
        for key, value in item.items():
            if 'S' in value:
                result[key] = value['S']
            elif 'N' in value:
                result[key] = int(value['N'])
            elif 'B' in value:
                result[key] = value['B']
        return result

