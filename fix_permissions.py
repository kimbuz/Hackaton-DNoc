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

def get_lambda_role():
    """Obtiene el rol de la función Lambda"""
    print("🔍 Obteniendo rol de Lambda...")
    
    cmd = "aws lambda get-function --function-name dnoc-chatbot-handler --region us-west-2 --query Configuration.Role --output text"
    success, role_arn = run_command(cmd)
    
    if success:
        role_name = role_arn.split('/')[-1]
        print(f"✅ Rol encontrado: {role_name}")
        return role_name
    else:
        print(f"❌ Error obteniendo rol: {role_arn}")
        return None

def add_bedrock_permissions(role_name):
    """Agrega permisos de Bedrock al rol"""
    print("🔧 Agregando permisos de Bedrock...")
    
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeAgent",
                    "bedrock:InvokeModel"
                ],
                "Resource": "*"
            }
        ]
    }
    
    # Crear archivo temporal con la política
    with open('bedrock_policy.json', 'w') as f:
        json.dump(policy_document, f, indent=2)
    
    # Agregar política al rol
    cmd = f"aws iam put-role-policy --role-name {role_name} --policy-name BedrockAgentAccess --policy-document file://bedrock_policy.json"
    success, output = run_command(cmd)
    
    if success:
        print("✅ Permisos de Bedrock agregados exitosamente")
        return True
    else:
        print(f"❌ Error agregando permisos: {output}")
        return False

def verify_permissions(role_name):
    """Verifica los permisos del rol"""
    print("🔍 Verificando permisos...")
    
    cmd = f"aws iam list-role-policies --role-name {role_name}"
    success, output = run_command(cmd)
    
    if success:
        policies = json.loads(output)
        print("📋 Políticas del rol:")
        for policy in policies['PolicyNames']:
            print(f"   - {policy}")
    
    # Verificar política específica
    cmd = f"aws iam get-role-policy --role-name {role_name} --policy-name BedrockAgentAccess --query PolicyDocument.Statement[0].Action --output json"
    success, actions = run_command(cmd)
    
    if success:
        try:
            action_list = json.loads(actions)
            print("✅ Permisos de Bedrock configurados:")
            for action in action_list:
                print(f"   - {action}")
        except:
            pass

def main():
    print("🔧 Corrigiendo permisos de Bedrock para Lambda...")
    print("=" * 50)
    
    # 1. Obtener rol de Lambda
    role_name = get_lambda_role()
    
    if role_name:
        # 2. Agregar permisos de Bedrock
        if add_bedrock_permissions(role_name):
            # 3. Verificar permisos
            verify_permissions(role_name)
            
            print("\n🎉 Permisos actualizados!")
            print("\n📝 Próximos pasos:")
            print("1. Espera 1-2 minutos para que se propaguen los permisos")
            print("2. Prueba la aplicación Gradio nuevamente")
        else:
            print("\n❌ Error actualizando permisos")
    else:
        print("\n❌ No se pudo obtener el rol de Lambda")

if __name__ == "__main__":
    main()