import boto3
import json

# Cliente Bedrock
bedrock_agent = boto3.client('bedrock-agent')

def create_agent():
    """Crea el agente de Bedrock para DNOC"""
    
    agent_config = {
        'agentName': 'dnoc-technical-assistant',
        'description': 'Asistente técnico especializado en resolución de incidentes DNOC',
        'foundationModel': 'anthropic.claude-3-haiku-20240307-v1:0',
        'instruction': """
Eres un asistente técnico especializado en DNOC (Data Network Operations Center).

Tu función es ayudar con:
- Resolución de incidentes de red y servicios
- Consultas sobre topología de equipos
- Procedimientos técnicos documentados
- Correlación de fallas y sistemas
- Respuestas rápidas para acciones correctivas

Características:
- Responde de forma concisa y técnica
- Prioriza soluciones rápidas
- Usa la base de conocimiento para consultar documentación
- Proporciona pasos específicos cuando sea posible
- Si no tienes información suficiente, solicita más detalles

Contexto DNOC:
- Manejas múltiples situaciones de falla en red/servicios
- Tienes acceso a Fault Managers con APIs
- Documentación en Confluence, PDFs y Word
- Inventarios de topología y relaciones de equipos
- Documentación técnica de resolución de problemas conocidos
        """,
        'idleSessionTTLInSeconds': 1800
    }
    
    try:
        response = bedrock_agent.create_agent(**agent_config)
        agent_id = response['agent']['agentId']
        print(f"Agente creado exitosamente: {agent_id}")
        return agent_id
    except Exception as e:
        print(f"Error creando agente: {e}")
        return None

def associate_knowledge_base(agent_id, knowledge_base_id):
    """Asocia la base de conocimiento al agente"""
    
    try:
        response = bedrock_agent.associate_agent_knowledge_base(
            agentId=agent_id,
            knowledgeBaseId=knowledge_base_id,
            description='Base de conocimiento técnico DNOC',
            knowledgeBaseState='ENABLED'
        )
        print("Base de conocimiento asociada exitosamente")
        return True
    except Exception as e:
        print(f"Advertencia: No se pudo asociar KB (usando modo mock): {e}")
        return False

def create_agent_alias(agent_id):
    """Crea un alias para el agente"""
    
    try:
        response = bedrock_agent.create_agent_alias(
            agentId=agent_id,
            agentAliasName='production',
            description='Alias de producción para DNOC Assistant'
        )
        alias_id = response['agentAlias']['agentAliasId']
        print(f"Alias creado exitosamente: {alias_id}")
        return alias_id
    except Exception as e:
        print(f"Error creando alias: {e}")
        return None

def prepare_agent(agent_id):
    """Prepara el agente para uso"""
    
    try:
        response = bedrock_agent.prepare_agent(agentId=agent_id)
        print("Agente preparado exitosamente")
        return True
    except Exception as e:
        print(f"Error preparando agente: {e}")
        return False

if __name__ == "__main__":
    # Crear agente completo
    agent_id = create_agent()
    if agent_id:
        prepare_agent(agent_id)
        alias_id = create_agent_alias(agent_id)
        print(f"\nConfiguraciones para Lambda:")
        print(f"AGENT_ID={agent_id}")
        print(f"AGENT_ALIAS_ID={alias_id}")