import boto3
import json
import uuid
from typing import Dict, List, Optional

class SquadModuloModel:
    def __init__(self):
        self.dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        self.table_name = 'SquadsModulos'
    
    def create_squad_modulo(self, data: Dict) -> Dict:
        """Cria um novo registro de squad/módulo"""
        squad_modulo_id = str(uuid.uuid4())
        
        item = {
            'squadModuloId': {'S': squad_modulo_id},
            'squad': {'S': data.get('squad', '')},
            'modulo': {'S': data.get('modulo', '')},
            'detalheEntrega': {'S': data.get('detalheEntrega', '')},
            'responsavel': {'S': data.get('responsavel', '')},
            'status': {'S': data.get('status', 'em andamento')},
            'reportarBug': {'S': data.get('reportarBug', '')},
            'regressivoId': {'S': data.get('regressivoId', '')}
        }
        
        self.dynamodb.put_item(TableName=self.table_name, Item=item)
        return {'squadModuloId': squad_modulo_id, **data}
    
    def get_squad_modulo(self, squad_modulo_id: str) -> Optional[Dict]:
        """Busca um registro de squad/módulo por ID"""
        try:
            response = self.dynamodb.get_item(
                TableName=self.table_name,
                Key={'squadModuloId': {'S': squad_modulo_id}}
            )
            
            if 'Item' in response:
                return self._deserialize_item(response['Item'])
            return None
        except Exception as e:
            print(f"Erro ao buscar squad/módulo: {e}")
            return None
    
    def list_squads_modulos_by_regressivo(self, regressivo_id: str) -> List[Dict]:
        """Lista todos os registros de squad/módulo de um regressivo"""
        try:
            response = self.dynamodb.query(
                TableName=self.table_name,
                IndexName='RegressivoIdIndex',
                KeyConditionExpression='regressivoId = :regressivo_id',
                ExpressionAttributeValues={
                    ':regressivo_id': {'S': regressivo_id}
                }
            )
            return [self._deserialize_item(item) for item in response.get('Items', [])]
        except Exception as e:
            print(f"Erro ao listar squads/módulos: {e}")
            return []
    
    def update_squad_modulo(self, squad_modulo_id: str, data: Dict) -> bool:
        """Atualiza um registro de squad/módulo"""
        try:
            update_expression = "SET "
            expression_attribute_values = {}
            
            for key, value in data.items():
                if key != 'squadModuloId':
                    update_expression += f"{key} = :{key}, "
                    expression_attribute_values[f":{key}"] = {'S': str(value)}
            
            update_expression = update_expression.rstrip(', ')
            
            self.dynamodb.update_item(
                TableName=self.table_name,
                Key={'squadModuloId': {'S': squad_modulo_id}},
                UpdateExpression=update_expression,
                ExpressionAttributeValues=expression_attribute_values
            )
            return True
        except Exception as e:
            print(f"Erro ao atualizar squad/módulo: {e}")
            return False
    
    def delete_squad_modulo(self, squad_modulo_id: str) -> bool:
        """Exclui um registro de squad/módulo"""
        try:
            self.dynamodb.delete_item(
                TableName=self.table_name,
                Key={'squadModuloId': {'S': squad_modulo_id}}
            )
            return True
        except Exception as e:
            print(f"Erro ao excluir squad/módulo: {e}")
            return False
    
    def create_squads_modulos_from_config(self, regressivo_id: str, squads_selecionadas: List[str]) -> bool:
        """Cria registros de squad/módulo baseado na configuração e squads selecionadas"""
        try:
            # Buscar configuração de squads
            config_model = ConfiguracaoModel()
            squads_config = config_model.get_squads_config()
            
            if not squads_config:
                return False
            
            # Criar registros para as squads selecionadas
            for squad_data in squads_config.get('squads', []):
                if squad_data['squad'] in squads_selecionadas:
                    for modulo in squad_data.get('modules', []):
                        if modulo:  # Verificar se o módulo não está vazio
                            self.create_squad_modulo({
                                'squad': squad_data['squad'],
                                'modulo': modulo,
                                'detalheEntrega': '',
                                'responsavel': '',
                                'status': 'em andamento',
                                'reportarBug': '',
                                'regressivoId': regressivo_id
                            })
            
            return True
        except Exception as e:
            print(f"Erro ao criar squads/módulos da configuração: {e}")
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


class ConfiguracaoModel:
    def __init__(self):
        self.dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        self.table_name = 'Configuracoes'
    
    def get_squads_config(self) -> Optional[Dict]:
        """Busca a configuração de squads e módulos"""
        try:
            response = self.dynamodb.get_item(
                TableName=self.table_name,
                Key={'configuracaoId': {'S': 'squads_e_modulos'}}
            )
            
            if 'Item' in response:
                data_str = response['Item']['data']['S']
                return json.loads(data_str)
            return None
        except Exception as e:
            print(f"Erro ao buscar configuração de squads: {e}")
            return None
    
    def update_squads_config(self, squads_data: Dict) -> bool:
        """Atualiza a configuração de squads e módulos"""
        try:
            self.dynamodb.put_item(
                TableName=self.table_name,
                Item={
                    'configuracaoId': {'S': 'squads_e_modulos'},
                    'data': {'S': json.dumps(squads_data)}
                }
            )
            return True
        except Exception as e:
            print(f"Erro ao atualizar configuração de squads: {e}")
            return False

