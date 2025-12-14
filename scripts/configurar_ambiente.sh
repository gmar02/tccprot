#!/usr/bin/env bash

echo "Exportando variáveis de ambiente..."
export RABBITMQ_URL=amqp://guest:guest@localhost:5672/
export TASK_QUEUE=ai_task_queue
export GEMINI_API_KEY=
echo "Variáveis exportadas!"
