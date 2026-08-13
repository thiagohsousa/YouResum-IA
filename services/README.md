# 🎥 Resumidor de Vídeos do YouTube com Groq AI

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-green?style=for-the-badge&logo=flask)
![Groq](https://img.shields.io/badge/Groq-Llama%203-orange?style=for-the-badge&logo=groq)
![License](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)

Aplicação Web de alta performance desenvolvida em **Python (Flask)** e integrada à API do **Groq** (utilizando a família de modelos **Llama 3**). O objetivo é realizar a extração, síntese e estruturação ultrarrápida de conteúdos de vídeos do YouTube em texto formatado.

O projeto foi projetado com foco em **resiliência e contingência de infraestrutura**, contando com arquitetura de fallback para extração de legendas, suporte a autenticação por sessão/cookies do YouTube e tratamento contra bloqueios de IP (anti-bot).

---

## 📌 Motivação e Contexto do Projeto

Este projeto foi construído para **uso pessoal utilitário**, resolvendo uma dor do dia a dia: otimizar o tempo de estudo e pesquisa extraindo rapidamente os pontos centrais de conteúdos audiovisuais extensos sem a necessidade de assistir a vídeos na íntegra.

A escolha do **Groq** como motor de IA garante inferências extremamente velozes (LPU™ Inference Engine), permitindo gerar resumos de transcrições longas em questão de segundos.

Durante o desenvolvimento, a aplicação evoluiu para lidar com cenários reais de engenharia de software:
- **Integração de Alta Performance:** Uso da biblioteca `groq` nativa em Python.
- **Restrições Anti-Bot do YouTube:** Implementação de fallback duplo utilizando `youtube-transcript-api` e `yt-dlp` com injeção de sessão local (`cookies.txt`).
- **Arquitetura Limpa:** Separação modular de rotas e serviços usando Blueprints do Flask.

---

## ✨ Funcionalidades Principais

- 📝 **Resumo Estruturado:** Gera uma síntese dividida em *Visão Geral*, *Pontos-Chave* e *Conclusão*.
- 📌 **Extração de Tópicos (Insights):** Mapeia os principais conceitos em marcadores legíveis.
- 🗺️ **Roadmap de Estudos:** Cria um guia passo a passo em ordem cronológica a partir do conteúdo.
- ⚡ **Entrada Flexível:** Aceita tanto URLs do YouTube (convencionais, encurtadas e Shorts) quanto colagem manual direta da transcrição.
- 🛡️ **Mecanismo de Contingência (Fallback):**
  1. *Plano A:* Extração ultrarrápida via `youtube-transcript-api`.
  2. *Plano B:* Extração de metadados estendidos via `yt-dlp` utilizando sessão ativa por cookies (`cookies.txt`).
  3. *Plano C:* Entrada manual de texto na interface web.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.10+, Flask, Blueprints
- **Inteligência Artificial:** Groq SDK (`groq`), Modelo `llama3-8b-8192` (ou `llama3-70b-8192`)
- **Extratores de Conteúdo:** `youtube-transcript-api`, `yt-dlp`
- **Gerenciamento de Ambiente:** `python-dotenv`, `venv`

---

## 📂 Estrutura Arquitetural do Projeto

Para garantir um código limpo e modular (Clean Architecture), o backend foi separado em responsabilidades bem definidas:

```text
YouResum/
│
├── routes/
│   └── main_routes.py     # Definição dos endpoints HTTP e lógica dos Blueprints
│
├── services/
│   ├── groq_service.py    # Comunicação e prompts para a API da Groq
│   └── youtube_service.py  # Extração de legendas, suporte a yt-dlp e cookies
│
├── templates/
│   └── index.html         # Interface do usuário (HTML5 / JS / Fetch API)
│
├── static/                # Arquivos estáticos (CSS / JS / Imagens)
│
├── .env                   # Variáveis de ambiente (Chave da API da Groq)
├── .gitignore             # Arquivos ignorados pelo Git (dados sensíveis/venv)
├── cookies.txt            # Sessão local do YouTube para bypass de bloqueio de IP
├── app.py                 # Ponto de entrada (Entry point) do servidor Flask
└── requirements.txt       # Lista de dependências do projeto