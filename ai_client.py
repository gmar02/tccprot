import os
import json
import pika
import requests
from typing import List

# ------------------------- Configuração RabbitMQ ----------------------------

RABBITMQ_URL = os.environ.get(
    "RABBITMQ_URL",
    "amqp://guest:guest@localhost:5672/"
)
TASK_QUEUE = os.environ.get("TASK_QUEUE", "ai_task_queue")

# ------------------------- Configuração Gemini -----------------------------

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={GEMINI_API_KEY}"

SYSTEM_PROMPT = """
Você é um assistente de IA especialista em análise de texto e classificação de demandas.
Sua tarefa é analisar um texto, criar um sumário conciso e classificá-lo em uma das categorias fornecidas.
Você DEVE retornar sua resposta em um formato JSON válido, de acordo com o schema solicitado.
O sumário deve ser em português e focado nos pontos principais e na ação necessária.
A confiabilidade deve ser um número flutuante entre 0.0 (totalmente incerto) e 1.0 (totalmente certo).
Analise o sentimento e a urgência no texto para ajudar na classificação.
"""

RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "sumario": {"type": "STRING", "description": "Um sumário conciso do texto original em português."},
        "categoria_sugerida": {"type": "STRING", "description": "A categoria mais apropriada da lista fornecida."},
        "confiabilidade": {"type": "NUMBER", "description": "Um score de confiança (0.0 a 1.0) para a categoria sugerida."}
    },
    "required": ["sumario", "categoria_sugerida", "confiabilidade"]
}

# ------------------------- Funções Gemini ----------------------------------

def analisar_demanda(text: str, categories: List[str]) -> dict:
    if not GEMINI_API_KEY:
        raise ValueError("Variável 'GEMINI_API_KEY' não foi configurada.")

    user_prompt = montar_prompt_usuario(text, categories)
    payload = montar_payload(user_prompt)

    return realizar_requisicao(payload)

def montar_prompt_usuario(texto_original: str, categorias: List[str]) -> str:
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
        "contents": [{"parts": [{"text": prompt_usuario}]}],
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": RESPONSE_SCHEMA,
            "temperature": 0.3
        }
    }

def realizar_requisicao(payload) -> dict:
    try:
        response = requests.post(GEMINI_URL, json=payload, timeout=45)
        response.raise_for_status()

        result = response.json()
        text_content = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '{}')

        if not text_content:
            raise Exception("Resposta da API Gemini estava vazia ou formatada incorretamente.")

        return json.loads(text_content)

    except Exception as e:
        raise Exception(f"Erro no cliente AI: {e} - Resposta da API: {result}")

# ------------------------- Funções RabbitMQ -------------------------------

def get_connection():
    params = pika.URLParameters(RABBITMQ_URL)
    return pika.BlockingConnection(params)

def processar_mensagem(ch, method, properties, body):
    """
    Lê a mensagem da fila, processa via Gemini e faz callback.
    """
    try:
        mensagem = json.loads(body)
        print(f"\n🟢 Processando demanda {mensagem['id_demanda']}")

        # Análise via Gemini
        resultado = analisar_demanda(
            mensagem["texto_original"],
            mensagem["categorias_disponiveis"]
        )

        print(f"✅ Resultado da IA para demanda {mensagem['id_demanda']}:")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

        # Se quiser fazer callback HTTP
        url_callback = mensagem.get("url_callback")
        if url_callback:
            callback_payload = {
                "id_demanda": mensagem["id_demanda"],
                "id_processamento": mensagem["id_processamento"],
                "resultado": resultado
            }
            try:
                resp = requests.post(url_callback, json=callback_payload, timeout=15)
                resp.raise_for_status()
                print(f"📤 Callback enviado com sucesso para {url_callback}")
            except Exception as e:
                print(f"⚠️ Erro no callback: {e}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f"❌ Erro ao processar mensagem: {e}")
        # Não dar ack para reprocessar depois
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

# ------------------------- Loop do consumidor -----------------------------

def main():
    connection = get_connection()
    channel = connection.channel()
    channel.queue_declare(queue=TASK_QUEUE, durable=True)

    print(f"🟢 Aguardando mensagens na fila '{TASK_QUEUE}'... CTRL+C para sair")
    channel.basic_consume(queue=TASK_QUEUE, on_message_callback=processar_mensagem)
    channel.start_consuming()

# ------------------------- Executável -------------------------------------

if __name__ == "__main__":
    main()

