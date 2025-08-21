# Backend - Lambda Function

Función Lambda que maneja las peticiones del frontend y se comunica con el agente de Bedrock.

## Variables de Entorno Requeridas

- `AGENT_ID`: ID del agente de Bedrock
- `AGENT_ALIAS_ID`: ID del alias del agente

## Despliegue

1. Crear archivo ZIP con lambda_function.py
2. Subir a AWS Lambda
3. Configurar variables de entorno
4. Asignar rol IAM con permisos de Bedrock