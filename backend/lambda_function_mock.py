import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    """Handler principal de Lambda con respuestas mock"""
    
    logger.info(f"Evento recibido: {json.dumps(event)}")
    
    try:
        # Parsear el body del request
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        message = body.get('message', '').lower()
        session_id = body.get('session_id', 'default-session')
        
        logger.info(f"Mensaje: {message}, Session ID: {session_id}")
        
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
        
        # Respuestas simuladas basadas en palabras clave
        response = get_mock_response(message)
        
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

def get_mock_response(message):
    """Genera respuestas simuladas basadas en el mensaje"""
    
    # Respuestas para problemas de conectividad
    if any(word in message for word in ["conectividad", "red", "conexion", "falla", "caida"]):
        return """🔧 **Procedimiento para Fallas de Conectividad:**

1. **Verificar estado de interfaces**
   - Revisar interfaces físicas y lógicas
   - Validar estado UP/DOWN

2. **Revisar logs de equipos**
   - Consultar logs de switches/routers
   - Buscar errores recientes

3. **Validar topología de red**
   - Verificar rutas de red
   - Confirmar VLAN y subnetting

4. **Ejecutar diagnósticos**
   - Ping, traceroute, telnet
   - Verificar DNS y DHCP

5. **Aplicar solución según tipo de falla**
   - Reinicio de interfaces si es necesario
   - Escalamiento a nivel 2 si persiste"""
    
    # Respuestas para reinicio de servicios
    elif any(word in message for word in ["reinicio", "servicio", "reiniciar", "restart"]):
        return """🔄 **Procedimiento para Reinicio de Servicios:**

1. **Identificar servicio afectado**
   - Verificar qué servicio presenta problemas
   - Revisar logs de aplicación

2. **Verificar dependencias**
   - Identificar servicios dependientes
   - Planificar orden de reinicio

3. **Ejecutar reinicio controlado**
   - Parar servicio gracefully
   - Esperar confirmación de parada
   - Iniciar servicio nuevamente

4. **Validar funcionamiento**
   - Verificar que el servicio responde
   - Probar funcionalidad básica

5. **Monitorear estabilidad**
   - Observar por 10-15 minutos
   - Confirmar que no hay errores"""
    
    # Respuestas para correlación de fallas
    elif any(word in message for word in ["correlacion", "fallas", "eventos", "alarmas"]):
        return """📊 **Procedimiento para Correlación de Fallas:**

1. **Recopilar eventos**
   - Obtener alarmas de múltiples sistemas
   - Revisar logs centralizados

2. **Aplicar reglas de correlación**
   - Usar herramientas de correlación
   - Identificar patrones temporales

3. **Identificar causa raíz**
   - Analizar secuencia de eventos
   - Determinar origen del problema

4. **Generar recomendaciones**
   - Proponer acciones correctivas
   - Priorizar por impacto

5. **Ejecutar acciones correctivas**
   - Implementar soluciones
   - Validar resolución del problema"""
    
    # Respuestas para topología
    elif any(word in message for word in ["topologia", "equipos", "inventario", "dispositivos"]):
        return """🗺️ **Información de Topología DNOC:**

**Consulta de Equipos:**
- Acceder al sistema de inventario
- Revisar diagramas de red actualizados
- Verificar relaciones entre dispositivos

**Herramientas Disponibles:**
- Sistema de gestión de topología
- Diagramas automáticos
- Base de datos de configuraciones

**Información Típica:**
- Switches, routers, firewalls
- Conexiones físicas y lógicas
- VLANs y subnets
- Puntos de falla críticos

¿Necesitas información específica de algún equipo o segmento de red?"""
    
    # Respuesta general
    else:
        return """👋 **Asistente DNOC - Modo Demo**

Soy tu asistente técnico DNOC. Puedo ayudarte con:

🔧 **Problemas de Conectividad**
- Diagnóstico de fallas de red
- Procedimientos de resolución

🔄 **Reinicio de Servicios**
- Pasos para reinicio controlado
- Validación post-reinicio

📊 **Correlación de Fallas**
- Análisis de eventos múltiples
- Identificación de causa raíz

🗺️ **Topología de Red**
- Consulta de equipos
- Información de conectividad

**Ejemplos de consultas:**
- "Tengo un problema de conectividad"
- "Necesito reiniciar un servicio"
- "Ayuda con correlación de fallas"

¿En qué puedo ayudarte hoy?"""
