import subprocess
import json

def run_command(cmd):
    """Ejecuta comando y retorna resultado"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)

def check_bedrock_enabled():
    """Verifica si Bedrock está habilitado en la región"""
    print("1️⃣ Verificando si Bedrock está habilitado...")
    
    cmd = "aws bedrock list-foundation-models --region us-west-2 --max-items 1"
    success, output = run_command(cmd)
    
    if success:
        print("✅ Bedrock está habilitado en us-west-2")
        return True
    else:
        print(f"❌ Bedrock no disponible: {output}")
        return False

def check_agent_exists():
    """Verifica si el agente existe"""
    print("\n2️⃣ Verificando si el agente existe...")
    
    # Obtener AGENT_ID de Lambda
    cmd = "aws lambda get-function-configuration --function-name dnoc-chatbot-handler --region us-west-2 --query Environment.Variables.AGENT_ID --output text"
    success, agent_id = run_command(cmd)
    
    if not success or agent_id == "None":
        print("❌ AGENT_ID no configurado en Lambda")
        return False, None
    
    print(f"📋 AGENT_ID: {agent_id}")
    
    # Verificar si el agente existe
    cmd = f"aws bedrock-agent get-agent --agent-id {agent_id} --region us-west-2"
    success, output = run_command(cmd)
    
    if success:
        print("✅ Agente existe en Bedrock")
        return True, agent_id
    else:
        print(f"❌ Agente no encontrado: {output}")
        return False, agent_id

def check_lambda_role_permissions():
    """Verifica permisos del rol de Lambda"""
    print("\n3️⃣ Verificando permisos del rol de Lambda...")
    
    # Obtener rol de Lambda
    cmd = "aws lambda get-function --function-name dnoc-chatbot-handler --region us-west-2 --query Configuration.Role --output text"
    success, role_arn = run_command(cmd)
    
    if not success:
        print(f"❌ Error obteniendo rol: {role_arn}")
        return False
    
    role_name = role_arn.split('/')[-1]
    print(f"📋 Rol de Lambda: {role_name}")
    
    # Verificar políticas del rol
    cmd = f"aws iam list-attached-role-policies --role-name {role_name}"
    success, attached = run_command(cmd)
    
    if success:
        policies = json.loads(attached)
        print("📋 Políticas adjuntas:")
        for policy in policies['AttachedPolicies']:
            print(f"   - {policy['PolicyName']}")
    
    # Verificar políticas inline
    cmd = f"aws iam list-role-policies --role-name {role_name}"
    success, inline = run_command(cmd)
    
    if success:
        policies = json.loads(inline)
        print("📋 Políticas inline:")
        for policy in policies['PolicyNames']:
            print(f"   - {policy}")
            
            # Mostrar contenido de política Bedrock
            if 'bedrock' in policy.lower():
                cmd_policy = f"aws iam get-role-policy --role-name {role_name} --policy-name {policy}"
                success_policy, policy_content = run_command(cmd_policy)
                if success_policy:
                    policy_doc = json.loads(policy_content)
                    print(f"     Acciones: {policy_doc['PolicyDocument']['Statement'][0]['Action']}")
    
    return True

def check_bedrock_agent_permissions():
    """Verifica si el usuario actual puede acceder a bedrock-agent"""
    print("\n4️⃣ Verificando acceso a bedrock-agent...")
    
    cmd = "aws bedrock-agent list-agents --region us-west-2 --max-results 1"
    success, output = run_command(cmd)
    
    if success:
        print("✅ Acceso a bedrock-agent OK")
        return True
    else:
        print(f"❌ Sin acceso a bedrock-agent: {output}")
        return False

def check_agent_status(agent_id):
    """Verifica el estado del agente"""
    print(f"\n5️⃣ Verificando estado del agente {agent_id}...")
    
    cmd = f"aws bedrock-agent get-agent --agent-id {agent_id} --region us-west-2 --query agent.agentStatus --output text"
    success, status = run_command(cmd)
    
    if success:
        print(f"📋 Estado del agente: {status}")
        if status != "PREPARED":
            print("⚠️ El agente debe estar en estado PREPARED para funcionar")
            return False
        return True
    else:
        print(f"❌ Error obteniendo estado: {status}")
        return False

def main():
    print("🔍 Diagnóstico completo de Bedrock Agent")
    print("=" * 50)
    
    issues = []
    
    # 1. Verificar Bedrock habilitado
    if not check_bedrock_enabled():
        issues.append("Bedrock no está habilitado en us-west-2")
    
    # 2. Verificar agente existe
    agent_exists, agent_id = check_agent_exists()
    if not agent_exists:
        issues.append("Agente no existe o AGENT_ID no configurado")
    
    # 3. Verificar permisos de Lambda
    check_lambda_role_permissions()
    
    # 4. Verificar acceso a bedrock-agent
    if not check_bedrock_agent_permissions():
        issues.append("Sin acceso a bedrock-agent API")
    
    # 5. Verificar estado del agente
    if agent_exists and agent_id:
        if not check_agent_status(agent_id):
            issues.append("Agente no está en estado PREPARED")
    
    print("\n" + "="*50)
    if issues:
        print("❌ PROBLEMAS ENCONTRADOS:")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
        
        print("\n🔧 PRÓXIMOS PASOS:")
        if "Bedrock no está habilitado" in str(issues):
            print("- Habilitar Bedrock en la consola AWS para us-west-2")
        if "Agente no existe" in str(issues):
            print("- Ejecutar: cd bedrock-agent && python agent_config.py")
        if "Sin acceso a bedrock-agent" in str(issues):
            print("- Verificar permisos IAM del usuario actual")
        if "no está en estado PREPARED" in str(issues):
            print("- Preparar el agente en la consola de Bedrock")
    else:
        print("✅ DIAGNÓSTICO COMPLETO - No se encontraron problemas obvios")
        print("El problema puede ser más específico. Revisar logs detallados.")

if __name__ == "__main__":
    main()