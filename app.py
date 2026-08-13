import os
import re
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

app = Flask(__name__)


def extrair_id_youtube(url):
    """Extrai o ID de 11 caracteres de URLs do YouTube."""
    padrao = r'(?:v=|\/([0-9A-Za-z_-]{11}).*|youtu\.be\/)([0-9A-Za-z_-]{11})'
    resultado = re.search(padrao, url)
    if resultado:
        return resultado.group(1) or resultado.group(2)
    return None


def obter_transcricao_yt_dlp(url):
    """Fallback usando yt-dlp quando o IP é bloqueado pelo transcript-api."""
    ydl_opts = {
        'skip_download': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['pt', 'en'],
        'quiet': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Tenta pegar legendas normais ou automáticas
            subtitles = info.get('subtitles') or info.get('automatic_captions')
            if not subtitles:
                return None, "O vídeo não possui legendas disponíveis."

            # Se pegou informações do vídeo (título e descrição)
            titulo = info.get('title', '')
            descricao = info.get('description', '')
            
            contexto = f"Título do Vídeo: {titulo}\n\nDescrição:\n{descricao}"
            return contexto, None
    except Exception as e:
        return None, str(e)


def obter_transcricao(video_id, url):
    """Busca as legendas tentando a biblioteca padrão e usando yt-dlp como fallback."""
    # Tentativa 1: youtube-transcript-api
    try:
        if hasattr(YouTubeTranscriptApi, 'get_transcript'):
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'pt-BR', 'en'])
        else:
            yt_api = YouTubeTranscriptApi()
            transcript_list = yt_api.fetch(video_id, languages=['pt', 'pt-BR', 'en'])

        texto = " ".join([item['text'] for item in transcript_list])
        return texto, None
    except Exception:
        # Tentativa 2: Fallback com yt-dlp caso o IP esteja bloqueado
        contexto, erro = obter_transcricao_yt_dlp(url)
        if contexto:
            return contexto, None
        
        return None, "O YouTube bloqueou a busca de legendas para este IP temporariamente. Tente outro vídeo ou aguarde alguns minutos."


def gerar_prompt_por_modo(modo):
    if modo == "roadmap":
        return "Você é um tutor especialista. Crie um ROADMAP PASSO A PASSO baseado neste conteúdo do vídeo."
    elif modo == "topicos":
        return "Você é um sintetizador de conteúdo. Extraia os PRINCIPAIS TÓPICOS e INSIGHTS deste vídeo em tópicos."
    else:
        return "Você é um assistente especialista. Crie um resumo estruturado contendo: Visão Geral, Pontos Chave e Conclusão."


def gerar_resposta_gemini(texto_conteudo, modo):
    instrucao = gerar_prompt_por_modo(modo)
    prompt = f"{instrucao}\n\nConteúdo/Transcrição do Vídeo:\n{texto_conteudo}"

    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt
    )
    return response.text


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/processar', methods=['POST'])
def processar():
    dados = request.get_json()
    
    # Permite receber a URL OU o texto direto da transcrição
    url = dados.get('url')
    texto_manual = dados.get('texto_manual')
    modo = dados.get('modo', 'resumo')

    # Caso o usuário tenha colado o texto direto
    if texto_manual and len(texto_manual.strip()) > 0:
        try:
            resposta = gerar_resposta_gemini(texto_manual, modo)
            return jsonify({"resposta": resposta})
        except Exception as e:
            return jsonify({"erro": f"Erro na API do Gemini: {str(e)}"}), 500

    # Validação padrão por URL
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
        return jsonify({"erro": f"Erro na API do Gemini: {str(e)}"}), 500

        
if __name__ == '__main__':
    app.run(debug=True)