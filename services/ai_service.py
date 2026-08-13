import os
from groq import Groq

def gerar_prompt_por_modo(modo):
    if modo == "roadmap":
        return "Você é um tutor especialista. Crie um ROADMAP PASSO A PASSO baseado neste conteúdo do vídeo."
    elif modo == "topicos":
        return "Você é um sintetizador de conteúdo. Extraia os PRINCIPAIS TÓPICOS e INSIGHTS deste vídeo em tópicos."
    else:
        return "Você é um assistente especialista. Crie um resumo estruturado contendo: Visão Geral, Pontos Chave e Conclusão."

def gerar_resposta_gemini(texto_conteudo, modo):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("Chave GROQ_API_KEY não encontrada no arquivo .env")

    client = Groq(api_key=api_key)
    
    instrucao = gerar_prompt_por_modo(modo)
    prompt_completo = f"{instrucao}\n\nConteúdo/Transcrição do Vídeo:\n{texto_conteudo}"

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt_completo}
        ],
        temperature=0.5,
    )
    
    return response.choices[0].message.content