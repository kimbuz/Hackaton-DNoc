import json
import boto3
import os
import logging
from botocore.exceptions import ClientError

# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Cliente Bedrock
bedrock_agent = boto3.client('bedrock-agent-runtime')

# Variables de entorno
AGENT_ID = os.environ['AGENT_ID']
AGENT_ALIAS_ID = os.environ['AGENT_ALIAS_ID']

def lambda_handler(event, context):
    """Handler principal de Lambda"""
    
    try:
        # Parsear el body del request
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        message = body.get('message', '')
        session_id = body.get('session_id', 'default-session')
        
        if not message:
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
        response = invoke_bedrock_agent(message, session_id)
        
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
    
    try:
        response = bedrock_agent.invoke_agent(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            sessionId=session_id,
            inputText=message
        )
        
        # Procesar respuesta streaming
        result = ""
        for event in response['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    result += chunk['bytes'].decode('utf-8')
        
        return result.strip()
        
    except ClientError as e:
        logger.error(f"Error de Bedrock: {e}")
        raise Exception(f"Error al comunicarse con Bedrock: {e}")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        raise Exception(f"Error inesperado: {e}")