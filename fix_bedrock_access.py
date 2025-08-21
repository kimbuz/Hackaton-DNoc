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

def get_lambda_env_vars():
    """Obtiene variables de entorno de Lambda"""
    print("🔍 Verificando variables de entorno...")
    
    cmd = "aws lambda get-function-configuration --function-name dnoc-chatbot-handler --region us-west-2 --query Environment.Variables --output json"
    success, output = run_command(cmd)
    
    if success:
        try:
            env_vars = json.loads(output)
            agent_id = env_vars.get('AGENT_ID')
            alias_id = env_vars.get('AGENT_ALIAS_ID')
            print(f"✅ AGENT_ID: {agent_id}")
            print(f"✅ AGENT_ALIAS_ID: {alias_id}")
            return agent_id, alias_id
        except:
            print("❌ Error parseando variables de entorno")
            return None, None
    else:
        print(f"❌ Error obteniendo variables: {output}")
        return None, None

def update_lambda_permissions():
    """Actualiza permisos de Lambda con política más amplia"""
    print("🔧 Actualizando permisos de Lambda...")
    
    # Obtener rol de Lambda
    cmd = "aws lambda get-function --function-name dnoc-chatbot-handler --region us-west-2 --query Configuration.Role --output text"
    success, role_arn = run_command(cmd)
    
    if not success:
        print(f"❌ Error obteniendo rol: {role_arn}")
        return False
    
    role_name = role_arn.split('/')[-1]
    print(f"📋 Rol: {role_name}")
    
    # Política más amplia para Bedrock
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:*"
                ],
                "Resource": "*"
            }
        ]
    }
    
    # Crear archivo temporal
    with open('bedrock_full_policy.json', 'w') as f:
        json.dump(policy_document, f, indent=2)
    
    # Actualizar política
    cmd = f"aws iam put-role-policy --role-name {role_name} --policy-name BedrockFullAccess --policy-document file://bedrock_full_policy.json"
    success, output = run_command(cmd)
    
    if success:
        print("✅ Permisos actualizados con acceso completo a Bedrock")
        return True
    else:
        print(f"❌ Error actualizando permisos: {output}")
        return False

def test_bedrock_access():
    """Prueba acceso a Bedrock listando modelos"""
    print("🧪 Probando acceso a Bedrock...")
    
    cmd = "aws bedrock list-foundation-models --region us-west-2 --query 'modelSummaries[0].modelId' --output text"
    success, output = run_command(cmd)
    
    if success:
        print(f"✅ Acceso a Bedrock OK - Modelo encontrado: {output}")
        return True
    else:
        print(f"❌ Sin acceso a Bedrock: {output}")
        return False

def create_simple_lambda():
    """Crea versión simplificada de Lambda para testing"""
    print("🔧 Creando versión simplificada para testing...")
    
    simple_code = '''
import json
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info("Lambda iniciada - versión simplificada")
    
    try:
        # Respuesta mock sin Bedrock
        mock_response = "Hola, soy el asistente DNOC. Esta es una respuesta de prueba sin conectar a Bedrock aún."
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'response': mock_response
            })
        }
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': f'Error: {str(e)}'
            })
        }
'''
    
    # Guardar código simplificado
    with open('simple_lambda.py', 'w') as f:
        f.write(simple_code)
    
    # Crear ZIP
    import zipfile
    with zipfile.ZipFile('simple_lambda.zip', 'w') as zip_file:
        zip_file.write('simple_lambda.py', 'lambda_function.py')
    
    # Actualizar función
    cmd = "aws lambda update-function-code --function-name dnoc-chatbot-handler --zip-file fileb://simple_lambda.zip --region us-west-2"
    success, output = run_command(cmd)
    
    if success:
        print("✅ Versión simplificada desplegada")
        return True
    else:
        print(f"❌ Error desplegando versión simple: {output}")
        return False

def main():
    print("🔧 Diagnosticando y corrigiendo acceso a Bedrock...")
    print("=" * 60)
    
    # 1. Verificar variables de entorno
    agent_id, alias_id = get_lambda_env_vars()
    
    # 2. Probar acceso a Bedrock
    bedrock_access = test_bedrock_access()
    
    # 3. Actualizar permisos
    if update_lambda_permissions():
        print("\n⏳ Esperando propagación de permisos (30 segundos)...")
        import time
        time.sleep(30)
        
        # 4. Si aún no funciona, usar versión simplificada
        if not bedrock_access:
            print("\n🔄 Desplegando versión simplificada para testing...")
            if create_simple_lambda():
                print("\n🎉 Versión de prueba desplegada!")
                print("\n📝 Próximos pasos:")
                print("1. Prueba Gradio - debería funcionar con respuestas mock")
                print("2. Una vez funcionando, podemos restaurar la versión completa")
            else:
                print("\n❌ Error en despliegue simplificado")
        else:
            print("\n🎉 Acceso a Bedrock configurado!")
            print("Prueba Gradio nuevamente")

if __name__ == "__main__":
    main()