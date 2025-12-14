#!/usr/bin/env  bash

echo "Derrubando servidor..."
sudo systemctl stop rabbitmq-server
echo "Servidor derrubado!"

echo "Desabilitando serviço..."
sudo systemctl disable rabbitmq-server
echo "Serviço desabilitado!"
