import json

# Simular Knowledge Base con documentos locales
MOCK_KNOWLEDGE_BASE = {
    "kb_id": "MOCK_KB_12345",
    "documents": {
        "procedimientos-dnoc": """
# Procedimientos DNOC - Resolución de Incidentes

## Fallas de Conectividad de Red
- Verificar estado de interfaces
- Revisar logs de equipos  
- Validar topología de red
- Ejecutar diagnósticos
- Aplicar solución según tipo de falla

## Reinicio de Servicios
- Identificar servicio afectado
- Verificar dependencias
- Ejecutar reinicio controlado
- Validar funcionamiento
- Monitorear estabilidad

## Correlación de Fallas
- Recopilar eventos
- Aplicar reglas de correlación
- Identificar causa raíz
- Generar recomendaciones
- Ejecutar acciones correctivas
        """
    }
}

def search_knowledge_base(query):
    """Simula búsqueda en knowledge base"""
    query_lower = query.lower()
    
    # Búsqueda simple por palabras clave
    if any(word in query_lower for word in ["conectividad", "red", "falla", "conexión"]):
        return "Para problemas de conectividad: 1) Verificar estado de interfaces 2) Revisar logs de equipos 3) Validar topología de red 4) Ejecutar diagnósticos 5) Aplicar solución según tipo de falla"
    
    elif any(word in query_lower for word in ["reinicio", "servicio", "reiniciar"]):
        return "Para reinicio de servicios: 1) Identificar servicio afectado 2) Verificar dependencias 3) Ejecutar reinicio controlado 4) Validar funcionamiento 5) Monitorear estabilidad"
    
    elif any(word in query_lower for word in ["correlación", "fallas", "eventos"]):
        return "Para correlación de fallas: 1) Recopilar eventos 2) Aplicar reglas de correlación 3) Identificar causa raíz 4) Generar recomendaciones 5) Ejecutar acciones correctivas"
    
    else:
        return "Consulta los procedimientos DNOC estándar o proporciona más detalles sobre el problema específico."

if __name__ == "__main__":
    print(f"✅ Mock Knowledge Base creado: {MOCK_KNOWLEDGE_BASE['kb_id']}")
    
    # Prueba
    test_query = "problema de conectividad en la red"
    result = search_knowledge_base(test_query)
    print(f"Consulta: {test_query}")
    print(f"Respuesta: {result}")