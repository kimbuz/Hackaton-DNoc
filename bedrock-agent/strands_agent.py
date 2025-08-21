from strands import Agent

def create_dnoc_agent():
    """Crea agente DNOC usando Strands con Claude Opus 4"""
    
    system_prompt = """
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
    
    agent = Agent(
        model="us.anthropic.claude-opus-4-20250514-v1:0",
        system_prompt=system_prompt
    )
    
    return agent

def process_message(message, session_id="default"):
    """Procesa mensaje usando el agente Strands"""
    
    try:
        agent = create_dnoc_agent()
        response = agent.run(message)
        return response
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