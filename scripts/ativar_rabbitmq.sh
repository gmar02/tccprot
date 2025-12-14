#!/usr/bin/env bash

echo "Habilitando servidor..."
sudo systemctl enable rabbitmq-server # habilita servidor RabbitMQ
echo "Servidor habilitado!"

echo "Iniciando servidor..."
sudo systemctl start rabbitmq-server # inicia servidor RabbitMQ
echo "Servidor iniciado!"

echo "Habilitando plugin de gerenciamento..."
sudo rabbitmq-plugins enable rabbitmq_management # habilita plugin de gerenciamento
echo "Plugin de gerenciamento habilitado!"

echo "Tudo pronto! Acesse em localhost:15672 (guest/guest)"
