import os
import re
from flask import Flask, render_template, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from google import genai
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

def extrair_id_youtube(url):
    """Extrai o ID de 11 caracteres de qualquer tipo de link do YouTube"""
    if not url:
        return None
    padrao = r'(?:v=|\/shorts\/|youtu\.be\/|\/v\/|\/embed\/|watch\?v=)([a-zA-Z0-9_-]{11})'
    match = re.search(padrao, url)
    return match.group(1) if match else None

def obter_transcricao(video_id):
    """Busca legendas de forma compatível com todas as versões do youtube-transcript-api"""
    try:
        # Tenta a sintaxe mais recente (list/get_transcript)
        if hasattr(YouTubeTranscriptApi, 'get_transcript'):
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'pt-BR', 'en'])
        else:
            # Para a versão 1.2+
            api = YouTubeTranscriptApi()
            fetched = api.fetch(video_id, languages=['pt', 'pt-BR', 'en'])
            transcript_list = fetched.element if hasattr(fetched, 'element') else fetched

        texto = " ".join([item['text'] for item in transcript_list])
        return texto, None

    except Exception as e:
        # Fallback de emergência sem restrição de idioma
        try:
            if hasattr(YouTubeTranscriptApi, 'get_transcript'):
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            else:
                api = YouTubeTranscriptApi()
                fetched = api.fetch(video_id)
                transcript_list = fetched.element if hasattr(fetched, 'element') else fetched

            texto = " ".join([item['text'] for item in transcript_list])
            return texto, None
        except Exception as e2:
            return None, f"Erro ao obter transcrição: {str(e2)}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/processar", methods=["POST"])
def processar():
    if not client:
        print("[ERRO] Chave da API GEMINI_API_KEY não foi encontrada no .env!")
        return jsonify({"erro": "Chave da API do Gemini não configurada no servidor."}), 500

    dados = request.get_json(silent=True) or {}
    url = dados.get("url", "").strip()
    modo = dados.get("modo", "resumo")

    print(f"\n--- Processando Requisição ---")
    print(f"URL recebida: '{url}'")
    print(f"Modo: '{modo}'")

    video_id = extrair_id_youtube(url)
    if not video_id:
        print(f"[ERRO 400] Não foi possível extrair o ID do vídeo da URL: {url}")
        return jsonify({"erro": "URL do YouTube inválida. Cole um link válido de vídeo ou Shorts."}), 400

    print(f"ID do vídeo extraído: {video_id}")
    transcricao, erro = obter_transcricao(video_id)

    if not transcricao:
        print(f"[ERRO 400] Falha na transcrição: {erro}")
        return jsonify({"erro": erro}), 400

    prompts = {
        "resumo": "Faça um resumo claro, conciso e objetivo do conteúdo deste vídeo em português. Use parágrafos bem estruturados.",
        "roadmap": "Com base na transcrição do vídeo, crie um Roadmap/Plano de Ação em formato de passo a passo cronológico com títulos e itens acionáveis.",
        "topicos": "Extraia os principais tópicos e pontos-chave discutidos no vídeo em uma lista clara (bullet points)."
    }

    instrucao = prompts.get(modo, prompts["resumo"])

    prompt_final = f"""
    Sua tarefa é analisar a transcrição de um vídeo do YouTube e gerar a resposta solicitada.
    
    Instrução: {instrucao}
    
    Transcrição do vídeo:
    {transcricao[:15000]}
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_final
        )
        return jsonify({
            "resposta": response.text,
            "video_id": video_id
        })
    except Exception as e:
        print(f"[ERRO 500] Erro ao chamar a API do Gemini: {str(e)}")
        return jsonify({"erro": f"Erro na IA: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)