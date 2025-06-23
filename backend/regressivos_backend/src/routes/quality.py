from flask import Blueprint, request, jsonify
from src.models.regressivo import RegressivoModel
from src.models.squad_modulo import SquadModuloModel
from datetime import datetime

quality_bp = Blueprint('quality', __name__)

@quality_bp.route('/regressivos', methods=['GET'])
def list_regressivos_ativos():
    """Lista todos os regressivos ativos"""
    try:
        regressivo_model = RegressivoModel()
        todos_regressivos = regressivo_model.list_regressivos()
        
        # Filtrar apenas regressivos ativos
        regressivos_ativos = [r for r in todos_regressivos if r.get('statusGeral') == 'ativo']
        
        return jsonify({'success': True, 'data': regressivos_ativos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@quality_bp.route('/regressivos/<regressivo_id>', methods=['GET'])
def get_regressivo_detalhes(regressivo_id):
    """Busca detalhes completos de um regressivo"""
    try:
        regressivo_model = RegressivoModel()
        squad_modulo_model = SquadModuloModel()
        
        regressivo = regressivo_model.get_regressivo(regressivo_id)
        if not regressivo:
            return jsonify({'success': False, 'error': 'Regressivo não encontrado'}), 404
        
        squads_modulos = squad_modulo_model.list_squads_modulos_by_regressivo(regressivo_id)
        
        # Verificar se SLA venceu
        sla_vencido = regressivo_model.verificar_sla_vencido(regressivo_id)
        
        # Calcular tempo restante do SLA
        tempo_restante = None
        if regressivo.get('slaFim') and not sla_vencido:
            sla_fim = datetime.fromisoformat(regressivo['slaFim'])
            agora = datetime.now()
            if sla_fim > agora:
                delta = sla_fim - agora
                horas = int(delta.total_seconds() // 3600)
                minutos = int((delta.total_seconds() % 3600) // 60)
                segundos = int(delta.total_seconds() % 60)
                tempo_restante = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        
        return jsonify({
            'success': True, 
            'data': {
                'regressivo': regressivo,
                'squads_modulos': squads_modulos,
                'sla_vencido': sla_vencido,
                'tempo_restante': tempo_restante
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@quality_bp.route('/squad-modulo/<squad_modulo_id>', methods=['PUT'])
def update_squad_modulo(squad_modulo_id):
    """Atualiza um registro de squad/módulo"""
    try:
        data = request.json
        
        # Verificar se o SLA não venceu antes de permitir edição
        squad_modulo_model = SquadModuloModel()
        squad_modulo = squad_modulo_model.get_squad_modulo(squad_modulo_id)
        
        if not squad_modulo:
            return jsonify({'success': False, 'error': 'Registro não encontrado'}), 404
        
        regressivo_model = RegressivoModel()
        sla_vencido = regressivo_model.verificar_sla_vencido(squad_modulo['regressivoId'])
        
        if sla_vencido:
            return jsonify({
                'success': False, 
                'error': 'SLA vencido. Não é possível editar este registro.'
            }), 403
        
        success = squad_modulo_model.update_squad_modulo(squad_modulo_id, data)
        
        if success:
            return jsonify({'success': True, 'message': 'Registro atualizado com sucesso'})
        else:
            return jsonify({'success': False, 'error': 'Erro ao atualizar registro'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@quality_bp.route('/squad-modulo/<squad_modulo_id>', methods=['GET'])
def get_squad_modulo(squad_modulo_id):
    """Busca um registro de squad/módulo por ID"""
    try:
        squad_modulo_model = SquadModuloModel()
        squad_modulo = squad_modulo_model.get_squad_modulo(squad_modulo_id)
        
        if not squad_modulo:
            return jsonify({'success': False, 'error': 'Registro não encontrado'}), 404
        
        # Verificar se SLA venceu
        regressivo_model = RegressivoModel()
        sla_vencido = regressivo_model.verificar_sla_vencido(squad_modulo['regressivoId'])
        
        return jsonify({
            'success': True, 
            'data': {
                'squad_modulo': squad_modulo,
                'sla_vencido': sla_vencido
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@quality_bp.route('/regressivos/<regressivo_id>/status-resumo', methods=['GET'])
def get_status_resumo(regressivo_id):
    """Busca resumo do status de um regressivo"""
    try:
        squad_modulo_model = SquadModuloModel()
        squads_modulos = squad_modulo_model.list_squads_modulos_by_regressivo(regressivo_id)
        
        # Contar status
        status_count = {
            'concluído': 0,
            'em andamento': 0,
            'bloqueado': 0,
            'concluido com bugs': 0
        }
        
        bugs_reportados = 0
        
        for item in squads_modulos:
            status = item.get('status', 'em andamento')
            if status in status_count:
                status_count[status] += 1
            
            if item.get('reportarBug'):
                bugs_reportados += 1
        
        total_itens = len(squads_modulos)
        progresso_percentual = 0
        
        if total_itens > 0:
            concluidos = status_count['concluído'] + status_count['concluido com bugs']
            progresso_percentual = round((concluidos / total_itens) * 100, 1)
        
        return jsonify({
            'success': True,
            'data': {
                'total_itens': total_itens,
                'status_count': status_count,
                'bugs_reportados': bugs_reportados,
                'progresso_percentual': progresso_percentual
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@quality_bp.route('/regressivos/<regressivo_id>/verificar-sla', methods=['GET'])
def verificar_sla(regressivo_id):
    """Verifica o status do SLA de um regressivo"""
    try:
        regressivo_model = RegressivoModel()
        regressivo = regressivo_model.get_regressivo(regressivo_id)
        
        if not regressivo:
            return jsonify({'success': False, 'error': 'Regressivo não encontrado'}), 404
        
        sla_vencido = regressivo_model.verificar_sla_vencido(regressivo_id)
        
        # Calcular tempo restante
        tempo_restante = None
        if regressivo.get('slaFim') and not sla_vencido:
            sla_fim = datetime.fromisoformat(regressivo['slaFim'])
            agora = datetime.now()
            if sla_fim > agora:
                delta = sla_fim - agora
                horas = int(delta.total_seconds() // 3600)
                minutos = int((delta.total_seconds() % 3600) // 60)
                segundos = int(delta.total_seconds() % 60)
                tempo_restante = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        
        return jsonify({
            'success': True,
            'data': {
                'sla_vencido': sla_vencido,
                'tempo_restante': tempo_restante,
                'sla_inicio': regressivo.get('slaInicio'),
                'sla_fim': regressivo.get('slaFim')
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

