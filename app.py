from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/teste', methods=['GET'])
def teste():
    return jsonify({"mensagem": "Teste concluído com sucesso!"}), 200

if __name__ == '__main__':
    print("Iniciando API...")
    app.run()