import os
import re
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi

def extrair_id_youtube(url):
    """Extrai o ID de 11 caracteres de URLs do YouTube (incluindo Shorts)."""
    padrao = r'(?:v=|\/([0-9A-Za-z_-]{11}).*|youtu\.be\/|shorts\/)([0-9A-Za-z_-]{11})'
    resultado = re.search(padrao, url)
    if resultado:
        return resultado.group(1) or resultado.group(2)
    return None

def obter_transcricao_yt_dlp(url):
    """Fallback usando yt-dlp apenas para leitura de metadados textuais sem checar mídias."""
    # Busca o cookies.txt localizado na raiz do projeto
    caminho_cookie = os.path.join(os.path.dirname(__file__), '..', 'cookies.txt')

    ydl_opts = {
        'skip_download': True,
        'quiet': True,
        'no_warnings': True,
        # O PONTO CHAVE: Força o yt-dlp a NÃO buscar formatos de vídeo/áudio
        'format': None,
        'check_formats': False,
        'extract_flat': 'in_playlist',
        'cookiefile': caminho_cookie if os.path.exists(caminho_cookie) else None,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            titulo = info.get('title', '')
            descricao = info.get('description', '')
            uploader = info.get('uploader', '')
            
            if not titulo and not descricao:
                return None, "Não foi possível extrair os metadados do vídeo."

            contexto = f"Título do Vídeo: {titulo}\nCanal: {uploader}\n\nDescrição:\n{descricao}"
            return contexto, None
    except Exception as e:
        return None, f"Erro ao extrair metadados: {str(e)}"

def obter_transcricao(video_id, url):
    """Busca as legendas tentando a biblioteca padrão e usando yt-dlp como fallback."""
    try:
        if hasattr(YouTubeTranscriptApi, 'get_transcript'):
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'pt-BR', 'en'])
        else:
            yt_api = YouTubeTranscriptApi()
            transcript_list = yt_api.fetch(video_id, languages=['pt', 'pt-BR', 'en'])

        texto = " ".join([item['text'] for item in transcript_list])
        return texto, None
    except Exception:
        # Fallback via yt-dlp com os cookies
        contexto, erro = obter_transcricao_yt_dlp(url)
        if contexto:
            return contexto, None
        
        return None, "Não foi possível extrair a legenda automaticamente para este vídeo."