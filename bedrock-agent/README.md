# Bedrock Agent - DNOC Assistant

Configuración del agente de Bedrock especializado en soporte técnico DNOC.

## Configuración del Agente

El agente está configurado con:
- **Modelo**: Claude 3 Haiku
- **Especialización**: Resolución de incidentes DNOC
- **Base de conocimiento**: Documentación técnica
- **Timeout**: 30 minutos de sesión

## Ejecución

```bash
python agent_config.py
```

Este script:
1. Crea el agente en Bedrock
2. Lo prepara para uso
3. Crea un alias de producción
4. Muestra las variables para Lambda

## Instrucciones del Agente

El agente está entrenado para:
- Resolver incidentes de red y servicios
- Consultar topología de equipos
- Acceder a documentación técnica
- Proporcionar soluciones rápidas
- Correlacionar fallas del sistema