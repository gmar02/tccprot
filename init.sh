#!/usr/bin/env bash

echo "Configurando ambiente virtual..."
source ./.venv/bin/activate
source ./scripts/configurar_ambiente.sh
echo "Ambiente virtual configurado!"

echo "Iniciando fila de mensagens..."
./scripts/ativar_rabbitmq.sh
echo "Fila de mensagens iniciada!"

echo "Acesse localhost:15672 (guest/guest)"

echo "Rode o comando 'flask run', 

./scripts/enviar_req_demo.sh, 

python3 ./ai_client.py"
