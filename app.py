import os
import uuid
import json
import pika
from flask import Flask, request, jsonify
from jsonschema import validate, ValidationError

# FLASK APP ###################################################################

app = Flask(__name__)

# RABBIT MQ ###################################################################

RABBITMQ_URL = os.environ.get("RABBITMQ_URL",
                              "amqp://guest:guest@localhost:5672/")
TASK_QUEUE = os.environ.get("TASK_QUEUE", "ai_task_queue")

def get_rabbitmq_connection():
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    return connection

# ROTAS #######################################################################

@app.route("/processar", methods=["POST"])
def processar_demanda():
    data = request.get_json()

    # validando JSON da requisição
    try:
        validar_json(data)
    except ValidationError as e:
        return {"Erro": "JSON inválido", "detalhe": e.message}, 400

    # criando mensagem para a fila de demandas
    demanda = criar_demanda(data)

    # publicando na fila de mensagens
    try:
        publicar_mensagem(demanda)
    except pika.exceptions.AMQPConnectionError as e:
        app.logger.error(f"Não foi possível conectar ao RabbitMQ: {e}")
        return jsonify({"Erro": "Serviço de enfileiramento indisponível"}), 503
    except Exception as e:
        app.logger.error(f"Erro ao publicar no RabbitMQ: {e}")
        return jsonify({"Erro", "Erro interno ao publicar demanda"}), 500

    # retornando ao cliente
    return jsonify({
        "id_processamento": demanda["id_processamento"],
        "id_demanda_cliente": data['id_demanda'],
        "status": "EM_FILA",
        "mensagem": "Demanda recebida e registrada. Seu processamento ocorrerá em breve."
    }), 202

# UTILITÁRIOS ##################################################################

def validar_json(data):
    request_model = {
        "type": "object",
        "properties": {
            "id_demanda": {"type": "string", "minLength": 1},
            "texto-original": {"type": "string", "minLength": 10},
            "categorias-disponiveis": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1
            },
            "url-callback": {"type": "string", "format": "uri"}
        },
        "required": ["id_demanda", "texto-original", "categorias-disponiveis", "url-callback"]
    }
    validate(instance=data, schema=request_model)

def criar_demanda(data):
    id_processamento = str(uuid.uuid4())
    return {
        "id_processamento": id_processamento,
        "id_demanda": data['id_demanda'],
        "texto_original": data['texto-original'],
        "categorias_disponiveis": data['categorias-disponiveis'],
        "url_callback": data['url-callback']
    }

def publicar_mensagem(mensagem):
    connection = get_rabbitmq_connection()
    channel = connection.channel()

    # Declare a durable queue (it will survive a RabbitMQ restart)
    channel.queue_declare(queue=TASK_QUEUE, durable=True)

    # Publish the message
    channel.basic_publish(
        exchange='',
        routing_key=TASK_QUEUE,
        body=json.dumps(mensagem),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
        )
    )

    connection.close()



###############################################################################

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
