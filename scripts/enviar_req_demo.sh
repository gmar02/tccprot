#!/usr/bin/env bash

curl -X POST http://localhost:5000/processar \
  -H "Content-Type: application/json" \
  -d '{
  "id_demanda": "123",
  "texto-original": "Este é um texto de teste com mais de 10 caracteres",
  "categorias-disponiveis": ["categoria1", "categoria2"],
  "url-callback": "http://localhost:5000/callback"
}'
