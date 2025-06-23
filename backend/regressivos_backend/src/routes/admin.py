from flask import Blueprint, request, jsonify
from src.models.regressivo import RegressivoModel
from src.models.squad_modulo import SquadModuloModel, ConfiguracaoModel
import google.generativeai as genai
import qrcode
import io
import base64
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# Configurar Gemini AI
genai.configure(api_key='AIzaSyA_dmMQb9pOglYE-O5325CdIqmoCloVSLI')

@admin_bp.route('/regressivos', methods=['GET'])
def list_regressivos():
    """Lista todos os regressivos"""
    try:
        regressivo_model = RegressivoModel()
        regressivos = regressivo_model.list_regressivos()
        return jsonify({'success': True, 'data': regressivos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/regressivos', methods=['POST'])
def create_regressivo():
    """Cria um novo regressivo"""
    try:
        data = request.json
        
        # Gerar QR codes
        qr_homolog = generate_qr_code(data.get('versaoHomolog', ''))
        qr_alpha = generate_qr_code(data.get('versaoAlpha', ''))
        
        data['qrCodeHomolog'] = qr_homolog
        data['qrCodeAlpha'] = qr_alpha
        
        regressivo_model = RegressivoModel()
        regressivo = regressivo_model.create_regressivo(data)
        
        # Criar registros de squad/módulo se squads foram selecionadas
        if 'squads_selecionadas' in data:
            squad_modulo_model = SquadModuloModel()
            squad_modulo_model.create_squads_modulos_from_config(
                regressivo['regressivoId'], 
                data['squads_selecionadas']
            )
        
        return jsonify({'success': True, 'data': regressivo})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/regressivos/<regressivo_id>', methods=['GET'])
def get_regressivo(regressivo_id):
    """Busca um regressivo por ID"""
    try:
        regressivo_model = RegressivoModel()
        regressivo = regressivo_model.get_regressivo(regressivo_id)
        
        if not regressivo:
            return jsonify({'success': False, 'error': 'Regressivo não encontrado'}), 404
        
        return jsonify({'success': True, 'data': regressivo})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/regressivos/<regressivo_id>', methods=['PUT'])
def update_regressivo(regressivo_id):
    """Atualiza um regressivo"""
    try:
        data = request.json
        regressivo_model = RegressivoModel()
        
        success = regressivo_model.update_regressivo(regressivo_id, data)
        
        if success:
            return jsonify({'success': True, 'message': 'Regressivo atualizado com sucesso'})
        else:
            return jsonify({'success': False, 'error': 'Erro ao atualizar regressivo'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/regressivos/<regressivo_id>', methods=['DELETE'])
def delete_regressivo(regressivo_id):
    """Exclui um regressivo"""
    try:
        regressivo_model = RegressivoModel()
        success = regressivo_model.delete_regressivo(regressivo_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Regressivo excluído com sucesso'})
        else:
            return jsonify({'success': False, 'error': 'Erro ao excluir regressivo'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/regressivos/<regressivo_id>/iniciar-sla', methods=['POST'])
def iniciar_sla(regressivo_id):
    """Inicia o SLA de um regressivo"""
    try:
        regressivo_model = RegressivoModel()
        success = regressivo_model.iniciar_sla(regressivo_id)
        
        if success:
            return jsonify({'success': True, 'message': 'SLA iniciado com sucesso'})
        else:
            return jsonify({'success': False, 'error': 'Erro ao iniciar SLA'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/regressivos/<regressivo_id>/parar-sla', methods=['POST'])
def parar_sla(regressivo_id):
    """Para o SLA de um regressivo"""
    try:
        regressivo_model = RegressivoModel()
        success = regressivo_model.parar_sla(regressivo_id)
        
        if success:
            return jsonify({'success': True, 'message': 'SLA parado com sucesso'})
        else:
            return jsonify({'success': False, 'error': 'Erro ao parar SLA'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/regressivos/<regressivo_id>/incluir-tempo', methods=['POST'])
def incluir_tempo_sla(regressivo_id):
    """Inclui mais tempo no SLA"""
    try:
        data = request.json
        horas = data.get('horas', 1)
        
        regressivo_model = RegressivoModel()
        success = regressivo_model.incluir_tempo_sla(regressivo_id, horas)
        
        if success:
            return jsonify({'success': True, 'message': f'{horas} horas adicionadas ao SLA'})
        else:
            return jsonify({'success': False, 'error': 'Erro ao incluir tempo no SLA'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/regressivos/<regressivo_id>/release-notes', methods=['POST'])
def gerar_release_notes(regressivo_id):
    """Gera release notes usando Gemini AI"""
    try:
        # Buscar dados do regressivo e squads/módulos
        regressivo_model = RegressivoModel()
        squad_modulo_model = SquadModuloModel()
        
        regressivo = regressivo_model.get_regressivo(regressivo_id)
        squads_modulos = squad_modulo_model.list_squads_modulos_by_regressivo(regressivo_id)
        
        if not regressivo:
            return jsonify({'success': False, 'error': 'Regressivo não encontrado'}), 404
        
        # Preparar prompt para o Gemini
        prompt = f"""
        Gere release notes profissionais para a release {regressivo.get('release', '')} da Ion Investimentos.
        
        Informações da Release:
        - Versão Homolog: {regressivo.get('versaoHomolog', '')}
        - Versão Alpha: {regressivo.get('versaoAlpha', '')}
        - Versão Firebase: {regressivo.get('versaoFirebase', '')}
        - Tipo de Release: {regressivo.get('tipoRelease', '')}
        - Plataforma: {regressivo.get('plataforma', '')}
        
        Entregas por Squad:
        """
        
        for item in squads_modulos:
            if item.get('detalheEntrega'):
                prompt += f"\n- {item.get('squad', '')}: {item.get('modulo', '')} - {item.get('detalheEntrega', '')}"
        
        prompt += """
        
        Por favor, gere release notes estruturadas com:
        1. Título da release
        2. Resumo executivo
        3. Principais funcionalidades e melhorias
        4. Correções de bugs (se houver)
        5. Informações técnicas relevantes
        6. Instruções de instalação/atualização (se aplicável)
        
        Use um tom profissional e técnico apropriado para uma empresa de investimentos.
        """
        
        # Gerar release notes com Gemini
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        release_notes = response.text
        
        return jsonify({
            'success': True, 
            'data': {
                'release_notes': release_notes,
                'generated_at': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/squads-config', methods=['GET'])
def get_squads_config():
    """Busca a configuração de squads e módulos"""
    try:
        config_model = ConfiguracaoModel()
        config = config_model.get_squads_config()
        
        if not config:
            return jsonify({'success': False, 'error': 'Configuração não encontrada'}), 404
        
        return jsonify({'success': True, 'data': config})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/squads-config', methods=['PUT'])
def update_squads_config():
    """Atualiza a configuração de squads e módulos"""
    try:
        data = request.json
        config_model = ConfiguracaoModel()
        
        success = config_model.update_squads_config(data)
        
        if success:
            return jsonify({'success': True, 'message': 'Configuração atualizada com sucesso'})
        else:
            return jsonify({'success': False, 'error': 'Erro ao atualizar configuração'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def generate_qr_code(text):
    """Gera QR code e retorna como base64"""
    if not text:
        return ""
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Converter para base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

