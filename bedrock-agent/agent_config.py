import boto3
import json

# Cliente Bedrock
bedrock_agent = boto3.client('bedrock-agent')

def create_or_get_agent():
    """Crea el agente de Bedrock para DNOC o usa el existente"""
    
    sts = boto3.client('sts')
    account_id = sts.get_caller_identity()['Account']
    role_arn = f'arn:aws:iam::{account_id}:role/service-role/AmazonBedrockExecutionRoleForKnowledgeBase_kb'
    
    # Primero intentar listar agentes existentes
    try:
        response = bedrock_agent.list_agents()
        for agent in response.get('agentSummaries', []):
            if agent['agentName'] == 'dnoc-technical-assistant':
                agent_id = agent['agentId']
                print(f"Actualizando agente existente: {agent_id}")
                
                # Actualizar el agente con roleArn
                try:
                    bedrock_agent.update_agent(
                        agentId=agent_id,
                        agentName='dnoc-technical-assistant',
                        description='Asistente técnico especializado en resolución de incidentes DNOC',
                        foundationModel='anthropic.claude-3-haiku-20240307-v1:0',
                        agentResourceRoleArn=role_arn,
                        instruction="""
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
                        """,
                        idleSessionTTLInSeconds=1800
                    )
                    print("Agente actualizado con roleArn")
                except Exception as update_error:
                    print(f"Error actualizando agente: {update_error}")
                
                return agent_id
    except Exception as e:
        print(f"Error listando agentes: {e}")
    
    # Si no existe, crear uno nuevo
    
    agent_config = {
        'agentName': 'dnoc-technical-assistant',
        'description': 'Asistente técnico especializado en resolución de incidentes DNOC',
        'foundationModel': 'anthropic.claude-3-haiku-20240307-v1:0',
        'agentResourceRoleArn': f'arn:aws:iam::{account_id}:role/service-role/AmazonBedrockExecutionRoleForKnowledgeBase_kb',
        'instruction': """
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
            agentVersion='DRAFT',
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
    import time
    
    # Crear o usar agente existente
    agent_id = create_or_get_agent()
    if agent_id:
        print("Esperando que el agente se complete...")
        time.sleep(10)
        
        if prepare_agent(agent_id):
            print("Esperando preparación del agente...")
            time.sleep(15)
            
            alias_id = create_agent_alias(agent_id)
            if alias_id:
                print(f"\n✅ Configuraciones para Lambda:")
                print(f"AGENT_ID={agent_id}")
                print(f"AGENT_ALIAS_ID={alias_id}")
                print(f"KB_MODE=mock")
            else:
                print("❌ Error creando alias")
        else:
            print("❌ Error preparando agente")
    else:
        print("❌ Error creando agente")