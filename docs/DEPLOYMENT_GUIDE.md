# Guía de Despliegue - DNOC Chatbot

## Prerrequisitos

- AWS CLI configurado con credenciales
- Python 3.12 instalado
- Acceso a Amazon Bedrock habilitado
- Permisos para crear recursos AWS

## Orden de Despliegue

### 1. Base de Conocimiento
```bash
cd knowledge-base
python setup_kb.py
```
**Salida esperada**: Knowledge Base ID

### 2. Agente Bedrock
```bash
cd bedrock-agent
python agent_config.py
```
**Salida esperada**: AGENT_ID y AGENT_ALIAS_ID

### 3. Infraestructura
```bash
cd infrastructure
python deploy.py
```
**Entrada requerida**: IDs del paso anterior
**Salida esperada**: API Endpoint

### 4. Frontend
```bash
cd frontend
set API_ENDPOINT=<endpoint-del-paso-anterior>
pip install -r requirements.txt
python app.py
```

## Verificación

1. **Base de conocimiento**: Verificar sincronización en consola Bedrock
2. **Agente**: Probar en Bedrock console
3. **API**: Hacer request POST al endpoint
4. **Frontend**: Acceder a http://localhost:7860

## Troubleshooting

### Error: "Access denied to Bedrock"
- Verificar que Bedrock esté habilitado en la región
- Revisar permisos IAM

### Error: "Knowledge base not found"
- Esperar a que termine la sincronización
- Verificar que los documentos estén en S3

### Error: "Lambda timeout"
- Aumentar timeout en CloudFormation
- Verificar logs en CloudWatch

## Variables de Entorno

```bash
# Frontend
API_ENDPOINT=https://your-api.execute-api.region.amazonaws.com/prod/chat

# Lambda (automático via CloudFormation)
AGENT_ID=XXXXXXXXXX
AGENT_ALIAS_ID=XXXXXXXXXX
```