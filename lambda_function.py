import json
import boto3
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
import qrcode
import io
import base64
import os
import google.generativeai as genai

# Configurar DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# Configurar Gemini AI
GEMINI_API_KEY = 'AIzaSyA_dmMQb9pOglYE-O5325CdIqmoCloVSLI'
genai.configure(api_key=GEMINI_API_KEY)

def decimal_default(obj):
    """Serializar Decimal para JSON"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def generate_qr_code(text):
    """Gerar QR Code em base64"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()

def lambda_handler(event, context):
    """Handler principal da Lambda"""
    try:
        http_method = event.get('httpMethod', '')
        path = event.get('path', '')
        path_parameters = event.get('pathParameters') or {}
        query_parameters = event.get('queryStringParameters') or {}
        body = event.get('body', '{}')
        
        # Parse do body se existir
        if body:
            try:
                body = json.loads(body)
            except:
                body = {}
        
        # Headers CORS
        cors_headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
        
        # Handle OPTIONS requests (CORS preflight)
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': ''
            }
        
        # Roteamento baseado no path
        if path == '/health':
            return {
                'statusCode': 200,
                'headers': cors_headers,
                'body': json.dumps({
                    'service': 'Ion Regressivos API',
                    'status': 'healthy'
                })
            }
        elif path.startswith('/api/admin/'):
            return handle_admin_routes(http_method, path, path_parameters, query_parameters, body, cors_headers)
        elif path.startswith('/api/quality/'):
            return handle_quality_routes(http_method, path, path_parameters, query_parameters, body, cors_headers)
        else:
            return {
                'statusCode': 404,
                'headers': cors_headers,
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

def handle_admin_routes(method, path, path_params, query_params, body, headers):
    """Gerenciar rotas administrativas"""
    
    if path == '/api/admin/regressivos':
        if method == 'GET':
            return list_regressivos(headers)
        elif method == 'POST':
            return create_regressivo(body, headers)
    
    elif path == '/api/admin/squads-config':
        if method == 'GET':
            return get_squads_config(headers)
        elif method == 'PUT':
            return update_squads_config(body, headers)
    
    elif path.startswith('/api/admin/regressivos/') and path_params.get('id'):
        regressivo_id = path_params['id']
        
        if method == 'GET':
            return get_regressivo(regressivo_id, headers)
        elif method == 'PUT':
            return update_regressivo(regressivo_id, body, headers)
        elif method == 'DELETE':
            return delete_regressivo(regressivo_id, headers)
    
    elif path.endswith('/iniciar-sla') and method == 'POST':
        regressivo_id = path_params.get('id')
        return iniciar_sla(regressivo_id, headers)
    
    elif path.endswith('/parar-sla') and method == 'POST':
        regressivo_id = path_params.get('id')
        return parar_sla(regressivo_id, headers)
    
    elif path.endswith('/incluir-tempo') and method == 'POST':
        regressivo_id = path_params.get('id')
        return incluir_tempo(regressivo_id, body, headers)
    
    elif path.endswith('/release-notes') and method == 'POST':
        regressivo_id = path_params.get('id')
        return generate_release_notes(regressivo_id, headers)
    
    return {
        'statusCode': 404,
        'headers': headers,
        'body': json.dumps({'error': 'Rota admin não encontrada'})
    }

def handle_quality_routes(method, path, path_params, query_params, body, headers):
    """Gerenciar rotas de qualidade"""
    
    if path == '/api/quality/regressivos':
        if method == 'GET':
            return list_active_regressivos(headers)
    
    elif path.startswith('/api/quality/regressivos/') and path_params.get('id'):
        regressivo_id = path_params['id']
        
        if method == 'GET':
            return get_regressivo_details(regressivo_id, headers)
    
    elif path.endswith('/status-resumo') and method == 'GET':
        regressivo_id = path_params.get('id')
        return get_status_resumo(regressivo_id, headers)
    
    elif path.endswith('/verificar-sla') and method == 'GET':
        regressivo_id = path_params.get('id')
        return verificar_sla(regressivo_id, headers)
    
    elif path.startswith('/api/quality/squad-modulo/') and path_params.get('id'):
        squad_modulo_id = path_params['id']
        
        if method == 'GET':
            return get_squad_modulo(squad_modulo_id, headers)
        elif method == 'PUT':
            return update_squad_modulo(squad_modulo_id, body, headers)
    
    return {
        'statusCode': 404,
        'headers': headers,
        'body': json.dumps({'error': 'Rota quality não encontrada'})
    }

# Funções administrativas
def list_regressivos(headers):
    """Listar todos os regressivos"""
    table = dynamodb.Table('Regressivos')
    response = table.scan()
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'success': True,
            'data': response.get('Items', [])
        }, default=decimal_default)
    }

def create_regressivo(data, headers):
    """Criar novo regressivo"""
    table = dynamodb.Table('Regressivos')
    squads_table = dynamodb.Table('SquadsModulos')
    
    regressivo_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    # Gerar QR codes
    qr_homolog = generate_qr_code(f"Homolog: {data.get('versaoHomolog')}")
    qr_alpha = generate_qr_code(f"Alpha: {data.get('versaoAlpha')}")
    
    # Criar item do regressivo
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
        'qrCodeHomolog': qr_homolog,
        'qrCodeAlpha': qr_alpha,
        'criadoEm': now
    }
    
    table.put_item(Item=item)
    
    # Criar entradas para squads selecionadas
    squads_selecionadas = data.get('squads', [])
    for squad_data in squads_selecionadas:
        for modulo in squad_data.get('modules', []):
            squad_modulo_item = {
                'squadModuloId': str(uuid.uuid4()),
                'regressivoId': regressivo_id,
                'squad': squad_data.get('squad'),
                'modulo': modulo,
                'status': 'em andamento',
                'detalheEntrega': '',
                'responsavel': '',
                'reportarBug': '',
                'criadoEm': now
            }
            squads_table.put_item(Item=squad_modulo_item)
    
    return {
        'statusCode': 201,
        'headers': headers,
        'body': json.dumps({
            'success': True,
            'data': item
        }, default=decimal_default)
    }

def get_squads_config(headers):
    """Buscar configuração de squads"""
    table = dynamodb.Table('Configuracoes')
    response = table.get_item(Key={'configuracaoId': 'squads_e_modulos'})
    
    if 'Item' in response:
        data = json.loads(response['Item']['data'])
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'data': data['squads']
            })
        }
    else:
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'error': 'Configuração não encontrada'})
        }

def update_squads_config(data, headers):
    """Atualizar configuração de squads"""
    table = dynamodb.Table('Configuracoes')
    
    config_data = {'squads': data.get('squads', [])}
    
    table.put_item(Item={
        'configuracaoId': 'squads_e_modulos',
        'data': json.dumps(config_data)
    })
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'success': True,
            'message': 'Configuração atualizada com sucesso'
        })
    }

def iniciar_sla(regressivo_id, headers):
    """Iniciar SLA do regressivo"""
    table = dynamodb.Table('Regressivos')
    
    now = datetime.now()
    sla_fim = now + timedelta(hours=24)
    
    table.update_item(
        Key={'regressivoId': regressivo_id},
        UpdateExpression='SET slaInicio = :inicio, slaFim = :fim',
        ExpressionAttributeValues={
            ':inicio': now.isoformat(),
            ':fim': sla_fim.isoformat()
        }
    )
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'success': True,
            'message': 'SLA iniciado com sucesso',
            'slaInicio': now.isoformat(),
            'slaFim': sla_fim.isoformat()
        })
    }

def generate_release_notes(regressivo_id, headers):
    """Gerar release notes com IA"""
    try:
        # Buscar dados do regressivo
        regressivos_table = dynamodb.Table('Regressivos')
        squads_table = dynamodb.Table('SquadsModulos')
        
        regressivo = regressivos_table.get_item(Key={'regressivoId': regressivo_id})
        if 'Item' not in regressivo:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Regressivo não encontrado'})
            }
        
        # Buscar squads e módulos
        squads_response = squads_table.query(
            IndexName='RegressivoIdIndex',
            KeyConditionExpression='regressivoId = :id',
            ExpressionAttributeValues={':id': regressivo_id}
        )
        
        # Preparar contexto para IA
        release_info = regressivo['Item']
        squads_info = squads_response.get('Items', [])
        
        context = f"""
        Release: {release_info.get('release')}
        Plataforma: {release_info.get('plataforma')}
        Versão Homolog: {release_info.get('versaoHomolog')}
        Versão Alpha: {release_info.get('versaoAlpha')}
        
        Squads e Módulos:
        """
        
        for squad in squads_info:
            context += f"- {squad.get('squad')}: {squad.get('modulo')} - {squad.get('detalheEntrega', 'Sem detalhes')}\n"
        
        # Gerar release notes com Gemini
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""
        Com base nas informações abaixo, gere release notes profissionais para a Ion Investimentos:
        
        {context}
        
        As release notes devem incluir:
        1. Título da release
        2. Resumo executivo
        3. Principais funcionalidades
        4. Melhorias técnicas
        5. Correções de bugs (se houver)
        6. Informações técnicas
        
        Use um tom profissional e técnico apropriado para uma empresa de investimentos.
        """
        
        response = model.generate_content(prompt)
        release_notes = response.text
        
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({
                'success': True,
                'data': {
                    'releaseNotes': release_notes,
                    'geradoEm': datetime.now().isoformat()
                }
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': f'Erro ao gerar release notes: {str(e)}'})
        }

# Funções de qualidade
def list_active_regressivos(headers):
    """Listar regressivos ativos"""
    table = dynamodb.Table('Regressivos')
    response = table.scan(
        FilterExpression='statusGeral = :status',
        ExpressionAttributeValues={':status': 'ativo'}
    )
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'success': True,
            'data': response.get('Items', [])
        }, default=decimal_default)
    }

def get_regressivo_details(regressivo_id, headers):
    """Buscar detalhes completos do regressivo"""
    regressivos_table = dynamodb.Table('Regressivos')
    squads_table = dynamodb.Table('SquadsModulos')
    
    # Buscar regressivo
    regressivo_response = regressivos_table.get_item(Key={'regressivoId': regressivo_id})
    if 'Item' not in regressivo_response:
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'error': 'Regressivo não encontrado'})
        }
    
    # Buscar squads/módulos
    squads_response = squads_table.query(
        IndexName='RegressivoIdIndex',
        KeyConditionExpression='regressivoId = :id',
        ExpressionAttributeValues={':id': regressivo_id}
    )
    
    # Verificar SLA
    regressivo = regressivo_response['Item']
    sla_vencido = False
    tempo_restante = None
    
    if regressivo.get('slaFim'):
        sla_fim = datetime.fromisoformat(regressivo['slaFim'])
        now = datetime.now()
        
        if now > sla_fim:
            sla_vencido = True
        else:
            delta = sla_fim - now
            tempo_restante = str(delta).split('.')[0]  # Remove microseconds
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'success': True,
            'data': {
                'regressivo': regressivo,
                'squads_modulos': squads_response.get('Items', []),
                'sla_vencido': sla_vencido,
                'tempo_restante': tempo_restante
            }
        }, default=decimal_default)
    }

def update_squad_modulo(squad_modulo_id, data, headers):
    """Atualizar status de squad/módulo"""
    # Primeiro, verificar se o SLA não venceu
    squads_table = dynamodb.Table('SquadsModulos')
    regressivos_table = dynamodb.Table('Regressivos')
    
    # Buscar squad/módulo
    squad_response = squads_table.get_item(Key={'squadModuloId': squad_modulo_id})
    if 'Item' not in squad_response:
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'error': 'Squad/Módulo não encontrado'})
        }
    
    squad_item = squad_response['Item']
    regressivo_id = squad_item['regressivoId']
    
    # Verificar SLA
    regressivo_response = regressivos_table.get_item(Key={'regressivoId': regressivo_id})
    if 'Item' in regressivo_response:
        regressivo = regressivo_response['Item']
        if regressivo.get('slaFim'):
            sla_fim = datetime.fromisoformat(regressivo['slaFim'])
            if datetime.now() > sla_fim:
                return {
                    'statusCode': 403,
                    'headers': headers,
                    'body': json.dumps({'error': 'SLA vencido. Não é possível editar.'})
                }
    
    # Atualizar item
    update_expression = 'SET '
    expression_values = {}
    
    if 'status' in data:
        update_expression += 'status = :status, '
        expression_values[':status'] = data['status']
    
    if 'detalheEntrega' in data:
        update_expression += 'detalheEntrega = :detalhe, '
        expression_values[':detalhe'] = data['detalheEntrega']
    
    if 'responsavel' in data:
        update_expression += 'responsavel = :resp, '
        expression_values[':resp'] = data['responsavel']
    
    if 'reportarBug' in data:
        update_expression += 'reportarBug = :bug, '
        expression_values[':bug'] = data['reportarBug']
    
    # Remover última vírgula
    update_expression = update_expression.rstrip(', ')
    
    squads_table.update_item(
        Key={'squadModuloId': squad_modulo_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values
    )
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'success': True,
            'message': 'Squad/Módulo atualizado com sucesso'
        })
    }

def get_status_resumo(regressivo_id, headers):
    """Obter resumo de status do regressivo"""
    squads_table = dynamodb.Table('SquadsModulos')
    
    response = squads_table.query(
        IndexName='RegressivoIdIndex',
        KeyConditionExpression='regressivoId = :id',
        ExpressionAttributeValues={':id': regressivo_id}
    )
    
    items = response.get('Items', [])
    total_itens = len(items)
    
    status_count = {}
    bugs_reportados = 0
    
    for item in items:
        status = item.get('status', 'em andamento')
        status_count[status] = status_count.get(status, 0) + 1
        
        if item.get('reportarBug'):
            bugs_reportados += 1
    
    concluidos = status_count.get('concluído', 0) + status_count.get('concluido com bugs', 0)
    progresso_percentual = (concluidos / total_itens * 100) if total_itens > 0 else 0
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'success': True,
            'data': {
                'total_itens': total_itens,
                'status_count': status_count,
                'bugs_reportados': bugs_reportados,
                'progresso_percentual': round(progresso_percentual, 1)
            }
        })
    }

def verificar_sla(regressivo_id, headers):
    """Verificar status do SLA"""
    table = dynamodb.Table('Regressivos')
    response = table.get_item(Key={'regressivoId': regressivo_id})
    
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'headers': headers,
            'body': json.dumps({'error': 'Regressivo não encontrado'})
        }
    
    regressivo = response['Item']
    sla_vencido = False
    tempo_restante = None
    
    if regressivo.get('slaFim'):
        sla_fim = datetime.fromisoformat(regressivo['slaFim'])
        now = datetime.now()
        
        if now > sla_fim:
            sla_vencido = True
        else:
            delta = sla_fim - now
            tempo_restante = str(delta).split('.')[0]
    
    return {
        'statusCode': 200,
        'headers': headers,
        'body': json.dumps({
            'success': True,
            'data': {
                'sla_vencido': sla_vencido,
                'tempo_restante': tempo_restante
            }
        })
    }

