# Infraestructura - DNOC Chatbot

Despliegue automatizado de la infraestructura AWS usando CloudFormation.

## Componentes Desplegados

- **Lambda Function**: Maneja requests del chatbot
- **API Gateway**: Endpoint REST para el frontend
- **IAM Roles**: Permisos necesarios para Bedrock
- **CORS**: Configuración para acceso web

## Despliegue

```bash
python deploy.py
```

El script solicitará:
- AGENT_ID (del agente de Bedrock)
- AGENT_ALIAS_ID (del alias del agente)

## Recursos Creados

- Stack CloudFormation: `dnoc-chatbot-stack`
- Lambda: `dnoc-chatbot-handler`
- API Gateway: `dnoc-chatbot-api`
- Rol IAM: `DNOCChatbotLambdaRole`

## Outputs

- **APIEndpoint**: URL para configurar en el frontend
- **LambdaFunctionName**: Nombre de la función Lambda