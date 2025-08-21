import boto3
import json

def create_dnoc_agent():
    """Crea cliente Bedrock para Claude Opus 4"""
    return boto3.client('bedrock-runtime', region_name='us-west-2')

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

Procedimientos DNOC conocidos:

FALLAS DE CONECTIVIDAD:
1. Verificar estado de interfaces
2. Revisar logs de equipos
3. Validar topología de red
4. Ejecutar diagnósticos
5. Aplicar solución según tipo de falla

REINICIO DE SERVICIOS:
1. Identificar servicio afectado
2. Verificar dependencias
3. Ejecutar reinicio controlado
4. Validar funcionamiento
5. Monitorear estabilidad

CORRELACIÓN DE FALLAS:
1. Recopilar eventos
2. Aplicar reglas de correlación
3. Identificar causa raíz
4. Generar recomendaciones
5. Ejecutar acciones correctivas

Características:
- Responde de forma concisa y técnica
- Prioriza soluciones rápidas
- Proporciona pasos específicos
- Si no tienes información suficiente, solicita más detalles
"""

def process_message(message, session_id="default"):
    """Procesa mensaje usando Claude Opus 4 directamente"""
    
    try:
        client = create_dnoc_agent()
        
        # Preparar mensaje para Claude
        messages = [
            {
                "role": "user",
                "content": message
            }
        ]
        
        # Invocar Claude Opus 4
        response = client.invoke_model(
            modelId='us.anthropic.claude-opus-4-20250514-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "system": get_system_prompt(),
                "messages": messages
            })
        )
        
        # Procesar respuesta
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
        
    except Exception as e:
        raise Exception(f"Error procesando mensaje: {str(e)}")

if __name__ == "__main__":
    # Prueba del agente
    test_message = "Tengo un problema de conectividad en la red"
    
    try:
        response = process_message(test_message)
        print(f"Consulta: {test_message}")
        print(f"Respuesta: {response}")
    except Exception as e:
        print(f"Error: {e}")