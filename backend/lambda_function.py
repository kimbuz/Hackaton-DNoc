import json
import os
import logging
import sys

# Agregar directorio bedrock-agent al path
sys.path.append('/opt/python')
sys.path.append(os.path.join(os.path.dirname(__file__), 'bedrock-agent'))

# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Log de inicio
logger.info("Lambda function iniciada con Strands Agent")

try:
    from claude_agent import process_message
    logger.info("Claude agent importado exitosamente")
except ImportError as e:
    logger.error(f"Error importando claude_agent: {e}")
    process_message = None

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
        
        # Invocar agente Claude
        logger.info("Invocando agente Claude")
        if process_message is None:
            raise Exception("Claude agent no disponible")
        
        response = process_message(message, session_id)
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

# Función invoke_bedrock_agent removida - ahora usa Strands