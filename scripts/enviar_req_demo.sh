#!/usr/bin/env bash

curl -X POST http://localhost:5000/processar \
  -H "Content-Type: application/json" \
  -d '{
    "id_demanda": "456",
    "texto-original": "Solicitamos a análise e correção de instabilidades recorrentes no módulo de faturamento do sistema ERP. Usuários relatam lentidão excessiva durante a emissão de notas fiscais, além de falhas intermitentes que resultam em erros de integração com a SEFAZ. O problema ocorre principalmente em horários de pico e impacta diretamente o fechamento financeiro diário. Também é necessário avaliar melhorias de performance, revisão de logs e validação das configurações de ambiente. Caso identificado, sugerimos a abertura de um plano de ação corretivo e preventivo.",
    "categorias-disponiveis": [
      "incidente",
      "problema_de_performance",
      "erro_de_sistema",
      "faturamento",
      "erp",
      "integracao_externa",
      "nota_fiscal",
      "impacto_financeiro",
      "manutencao_corretiva",
      "melhoria_continua",
      "suporte_tecnico"
    ],
    "url-callback": "http://localhost:5000/callback"
  }'
