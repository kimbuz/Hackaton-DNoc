import json
import boto3
import os
import logging
from botocore.exceptions import ClientError

# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Log de inicio
logger.info("Lambda function iniciada")
logger.info(f"Variables de entorno: AGENT_ID={os.environ.get('AGENT_ID')}, AGENT_ALIAS_ID={os.environ.get('AGENT_ALIAS_ID')}")

# Cliente Bedrock
bedrock_agent = boto3.client('bedrock-agent-runtime')

# Variables de entorno
AGENT_ID = os.environ['AGENT_ID']
AGENT_ALIAS_ID = os.environ['AGENT_ALIAS_ID']

def lambda_handler(event, context):
    """Handler principal de Lambda"""
    
    logger.info(f"Evento recibido: {json.dumps(event)}")
    
    try:
        # Parsear el body del request
        logger.info("Parseando body del request")
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
            logger.info(f"Body parseado desde string: {body}")
        else:
            body = event.get('body', {})
            logger.info(f"Body directo: {body}")
        
        message = body.get('message', '')
        session_id = body.get('session_id', 'default-session')
        
        logger.info(f"Mensaje: {message}, Session ID: {session_id}")
        
        if not message:
            logger.warning("Mensaje vacío recibido")
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Mensaje requerido'
                })
            }
        
        # Invocar agente de Bedrock
        logger.info("Invocando agente de Bedrock")
        response = invoke_bedrock_agent(message, session_id)
        logger.info(f"Respuesta del agente: {response[:100]}...")  # Primeros 100 chars
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'response': response,
                'session_id': session_id
            })
        }
        
    except Exception as e:
        logger.error(f"Error en lambda_handler: {str(e)}")
        logger.error(f"Tipo de error: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': f'Error interno: {str(e)}'
            })
        }

def invoke_bedrock_agent(message, session_id):
    """Invoca el agente de Bedrock y retorna la respuesta"""
    
    logger.info(f"Invocando agente - ID: {AGENT_ID}, Alias: {AGENT_ALIAS_ID}")
    
    try:
        response = bedrock_agent.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=message
        )
        logger.info("Respuesta de Bedrock recibida exitosamente")
        
        # Procesar respuesta streaming
        result = ""
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    result += chunk['bytes'].decode('utf-8')
        
        return result.strip()
        
    except ClientError as e:
        logger.error(f"Error de Bedrock ClientError: {e}")
        logger.error(f"Error code: {e.response.get('Error', {}).get('Code', 'Unknown')}")
        logger.error(f"Error message: {e.response.get('Error', {}).get('Message', 'Unknown')}")
        raise Exception(f"Error al comunicarse con Bedrock: {e}")
    except Exception as e:
        logger.error(f"Error inesperado en invoke_bedrock_agent: {e}")
        logger.error(f"Tipo de error: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise Exception(f"Error inesperado: {e}")