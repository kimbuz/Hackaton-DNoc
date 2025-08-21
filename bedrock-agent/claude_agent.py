import boto3
import json

def create_dnoc_agent():
    """Crea cliente Bedrock para Knowledge Base"""
    return boto3.client('bedrock-agent-runtime', region_name='us-west-2')

def get_system_prompt():
    """Retorna el prompt del sistema para DNOC"""
    return """
Eres un asistente técnico especializado en DNOC (Data Network Operations Center).

Tu función es ayudar con:
- Resolución de incidentes de red y servicios
- Consultas sobre topología de equipos
- Procedimientos técnicos documentados
- Correlación de fallas y sistemas
- Respuestas rápidas para acciones correctivas

Usa la información de la base de conocimiento cuando esté disponible.
Proporciona respuestas técnicas, concisas y con pasos específicos.
"""

def process_message(message, session_id="default"):
    """Procesa mensaje usando Knowledge Base directamente"""
    
    try:
        client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
        
        # Usar retrieve_and_generate con Knowledge Base
        response = client.retrieve_and_generate(
            input={
                'text': message
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': 'YIQHGCIFHL',
                    'modelArn': 'arn:aws:bedrock:us-west-2::foundation-model/amazon.titan-embed-text-v2:0'
                }
            }
        )
        
        return response['output']['text']
        
    except Exception as e:
        # Fallback directo a Claude
        try:
            bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')
            
            response = bedrock_runtime.invoke_model(
                modelId='us.anthropic.claude-sonnet-4-20250514-v1:0',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "system": get_system_prompt(),
                    "messages": [{"role": "user", "content": message}]
                })
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as fallback_error:
            raise Exception(f"Error con KB: {str(e)}, Fallback: {str(fallback_error)}")

if __name__ == "__main__":
    test_message = "Tengo un problema de conectividad en la red"
    try:
        response = process_message(test_message)
        print(f"Consulta: {test_message}")
        print(f"Respuesta: {response}")
    except Exception as e:
        print(f"Error: {e}")
