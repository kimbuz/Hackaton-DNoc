# Configuración Manual de Knowledge Base

## Paso 1: Crear Knowledge Base en Consola AWS

1. **Ir a Amazon Bedrock Console**
   - Navegar a: https://console.aws.amazon.com/bedrock/
   - Región: us-west-2

2. **Crear Knowledge Base**
   - Click "Knowledge bases" → "Create knowledge base"
   - Name: `dnoc-technical-kb`
   - Description: `Base de conocimiento técnico para DNOC`
   - IAM Role: Seleccionar `AmazonBedrockExecutionRoleForKnowledgeBase_kb`

3. **Configurar Data Source**
   - Data source name: `dnoc-documents`
   - S3 URI: `s3://dnoc-knowledge-base-docs/documents/`
   - Chunking strategy: Default chunking
   - Max tokens: 300
   - Overlap percentage: 20%

4. **Vector Database**
   - Seleccionar: "Quick create a new vector store - Recommended"
   - Esto creará automáticamente un vector store administrado por AWS
   - NO seleccionar OpenSearch Serverless

5. **Review and Create**
   - Revisar configuración
   - Click "Create knowledge base"
   - Esperar 5-10 minutos para que se complete la creación
   - Esperar a que la sincronización termine (puede tomar otros 5-10 minutos)

## Verificación

1. **Estado de Knowledge Base**: Debe mostrar "Ready"
2. **Data Source**: Debe mostrar "Available" 
3. **Sync Status**: Debe mostrar "Completed"

## Resultado Esperado

- Knowledge Base ID (ejemplo: `ABCD1234EF`)
- Vector store creado automáticamente
- Documentos indexados y listos para consultas

## Siguiente Paso

Una vez creada la KB, anotar el Knowledge Base ID y continuar con:
```bash
cd ../bedrock-agent
python agent_config.py
```