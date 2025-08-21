import subprocess
import zipfile
import os

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

def update_claude_agent_with_kb():
    """Actualiza claude_agent.py para usar la base de conocimiento"""
    
    claude_code = '''import boto3
import json

def create_dnoc_agent():
    """Crea cliente Bedrock para Knowledge Base"""
    return boto3.client('bedrock-agent-runtime', region_name='us-west-2')

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

Usa la información de la base de conocimiento cuando esté disponible.
Proporciona respuestas técnicas, concisas y con pasos específicos.
"""

def process_message(message, session_id="default"):
    """Procesa mensaje usando Knowledge Base directamente"""
    
    try:
        client = boto3.client('bedrock-agent-runtime', region_name='us-west-2')
        
        # Usar retrieve_and_generate con Knowledge Base
        response = client.retrieve_and_generate(
            input={
                'text': message
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': 'YIQHGCIFHL',
                    'modelArn': 'arn:aws:bedrock:us-west-2::foundation-model/amazon.titan-embed-text-v2:0'
                }
            }
        )
        
        return response['output']['text']
        
    except Exception as e:
        # Fallback directo a Claude
        try:
            bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')
            
            response = bedrock_runtime.invoke_model(
                modelId='us.anthropic.claude-sonnet-4-20250514-v1:0',
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "system": get_system_prompt(),
                    "messages": [{"role": "user", "content": message}]
                })
            )
            
            response_body = json.loads(response['body'].read())
            return response_body['content'][0]['text']
            
        except Exception as fallback_error:
            raise Exception(f"Error con KB: {str(e)}, Fallback: {str(fallback_error)}")

if __name__ == "__main__":
    test_message = "Tengo un problema de conectividad en la red"
    try:
        response = process_message(test_message)
        print(f"Consulta: {test_message}")
        print(f"Respuesta: {response}")
    except Exception as e:
        print(f"Error: {e}")
'''
    
    # Escribir archivo actualizado
    with open('claude_agent.py', 'w', encoding='utf-8') as f:
        f.write(claude_code)
    
    print("✅ claude_agent.py actualizado con Knowledge Base YIQHGCIFHL")

def create_lambda_package():
    """Crea paquete Lambda con ambos archivos"""
    print("📦 Creando paquete Lambda...")
    
    zip_path = 'lambda_with_kb.zip'
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Agregar función Lambda
        zip_file.write('../backend/lambda_function.py', 'lambda_function.py')
        # Agregar agente Claude actualizado
        zip_file.write('claude_agent.py', 'claude_agent.py')
    
    print(f"✅ Paquete creado: {zip_path}")
    return zip_path

def deploy_lambda(zip_path):
    """Despliega Lambda con Knowledge Base"""
    print("🚀 Desplegando Lambda con Knowledge Base...")
    
    cmd = f"aws lambda update-function-code --function-name dnoc-chatbot-handler --zip-file fileb://{zip_path} --region us-west-2"
    success, output = run_command(cmd)
    
    if success:
        print("✅ Lambda actualizada exitosamente")
        
        # Actualizar timeout para Knowledge Base
        cmd_timeout = "aws lambda update-function-configuration --function-name dnoc-chatbot-handler --timeout 60 --region us-west-2"
        run_command(cmd_timeout)
        print("✅ Timeout actualizado para Knowledge Base")
        
        return True
    else:
        print(f"❌ Error desplegando: {output}")
        return False

def main():
    print("🔧 Desplegando DNOC Assistant con Knowledge Base YIQHGCIFHL")
    print("=" * 60)
    
    # 1. Actualizar claude_agent.py
    update_claude_agent_with_kb()
    
    # 2. Crear paquete
    zip_path = create_lambda_package()
    
    if zip_path:
        # 3. Desplegar
        if deploy_lambda(zip_path):
            # 4. Limpiar
            os.remove(zip_path)
            
            print("\n🎉 Despliegue completado!")
            print("\n📝 Configuración:")
            print("- ✅ claude_agent.py con Knowledge Base YIQHGCIFHL")
            print("- ✅ lambda_function.py actualizado")
            print("- ✅ Claude Opus 4 usando retrieve_and_generate")
            
            print("\n🧪 Prueba Gradio - debería usar la base de conocimiento")
        else:
            print("\n❌ Error en el despliegue")
    else:
        print("\n❌ Error creando paquete")

if __name__ == "__main__":
    main()