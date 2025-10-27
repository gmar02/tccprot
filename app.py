from flask import Flask, jsonify, make_response
import logging as pylogging
from prototipo import processar

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

# ROTAS #######################################################################

@app.route('/teste', methods=['GET'])
def teste():
    payload = processar()
    resposta = make_response(jsonify(payload))
    resposta.headers["Content-Type"] = "application/json; charset=utf-8"
    return resposta

###############################################################################

if __name__ == '__main__':
    # desativando logging do servidor de desenvolvimento
    log = pylogging.getLogger("werkzeug")
    log.setLevel(pylogging.ERROR)

    print("Iniciando API em servidor de desenvolvimento...")
    print("API iniciada em http://0.0.0.0:5000")

    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
