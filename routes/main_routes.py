from flask import Blueprint, render_template, request, jsonify
from services.ai_service import gerar_resposta_gemini
from services.youtube_service import extrair_id_youtube, obter_transcricao

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@main_bp.route('/processar', methods=['POST'])
def processar():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Nenhum dado enviado."}), 400
    
    url = dados.get('url')
    texto_manual = dados.get('texto_manual')
    modo = dados.get('modo', 'resumo')

    # 1. Fluxo de transcrição manual
    if texto_manual and len(texto_manual.strip()) > 0:
        try:
            resposta = gerar_resposta_gemini(texto_manual, modo)
            return jsonify({"resposta": resposta})
        except Exception as e:
            return jsonify({"erro": f"Erro na API do Gemini: {str(e)}"}), 500

    # 2. Fluxo normal por URL do YouTube
    if not url:
        return jsonify({"erro": "Por favor, envie a URL do vídeo ou o texto da transcrição."}), 400

    video_id = extrair_id_youtube(url)
    if not video_id:
        return jsonify({"erro": "URL do YouTube inválida."}), 400

    texto_conteudo, erro = obter_transcricao(video_id, url)

    if erro:
        return jsonify({"erro": f"{erro} Dica: Você também pode colar o texto da legenda manualmente."}), 400

    try:
        resposta = gerar_resposta_gemini(texto_conteudo, modo)
        return jsonify({
            "resposta": resposta,
            "video_id": video_id
        })
    except Exception as e:
        msg = str(e)
        if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
            return jsonify({"erro": "Cota do Gemini excedida temporariamente. Aguarde 1 minuto."}), 429
        return jsonify({"erro": f"Erro na API do Gemini: {msg}"}), 500