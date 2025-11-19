import os
import requests
import json

# CONFIGURAÇÃO GEMINI ##########################################################
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={GEMINI_API_KEY}"

# PROMPT #######################################################################
SYSTEM_PROMPT = """
Você é um assistente de IA especialista em análise de texto e classificação de demandas.
Sua tarefa é analisar um texto, criar um sumário conciso e classificá-lo em uma das categorias fornecidas.
Você DEVE retornar sua resposta em um formato JSON válido, de acordo com o schema solicitado.
O sumário deve ser em português e focado nos pontos principais e na ação necessária.
A confiabilidade deve ser um número flutuante entre 0.0 (totalmente incerto) e 1.0 (totalmente certo).
Analise o sentimento e a urgência no texto para ajudar na classificação.
"""

# MODELO RESPOSTA ##############################################################
RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "sumario": {
            "type": "STRING",
            "description": "Um sumário conciso do texto original em português."
        },
        "categoria_sugerida": {
            "type": "STRING",
            "description": "A categoria mais apropriada da lista fornecida."
        },
        "confiabilidade": {
            "type": "NUMBER",
            "description": "Um score de confiança (0.0 a 1.0) para a categoria sugerida."
        }
    },
    "required": ["sumario", "categoria_sugerida", "confiabilidade"]
}

# PROCESSADOR ##################################################################
def analisar_demanda(text: str, categories: list) -> dict:
    if not GEMINI_API_KEY:
        raise ValueError("Variável 'GEMINI_API_KEY' não foi configurada.")

    user_prompt = montar_prompt_usuario(text, categories)
    payload = montar_payload(user_prompt)

    result = realizar_requisicao(payload)
    return result

# UTILITÁRIOS ##################################################################
def montar_prompt_usuario(texto_original: str, categorias: list[str]) -> str:
    return f"""
    Por favor, analise o texto abaixo e classifique-o.

    **Texto Original:**
    "{texto_original}"

    **Categorias Disponíveis:**
    {json.dumps(categorias)}

    Forneça sua análise no formato JSON solicitado.
    """

def montar_payload(prompt_usuario: str) -> dict:
    return {
        "contents": [
            {
                "parts": [{"text": prompt_usuario}]
            }
        ],
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA,
            "temperature": 0.3
        }
    }

def realizar_requisicao(payload) -> dict:
    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=45)
        response.raise_for_status()  # Lança erro para status HTTP 4xx/5xx

        result = response.json()

        # Extrai o conteúdo de texto da primeira "candidate"
        # O Gemini retorna o JSON como uma “string” de texto, que precisa ser parseada
        text_content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '{}')

        if not text_content:
            raise Exception("Resposta da API Gemini estava vazia ou formatada incorretamente.")

        # Parseia a string JSON para um dicionário Python
        return json.loads(text_content)

    except Exception as e:
        raise Exception(f"Erro inesperado no cliente AI: {e} - Resposta da API: {result}")
