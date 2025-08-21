import subprocess
import os
import zipfile
import json

def run_command(cmd, cwd=None):
    """Ejecuta comando y retorna resultado"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)

def create_lambda_zip():
    """Crea ZIP con el código Lambda"""
    print("📦 Creando ZIP con código Lambda...")
    
    zip_path = "backend/lambda_code.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        zip_file.write('backend/lambda_function.py', 'lambda_function.py')
    
    print(f"✅ ZIP creado: {zip_path}")
    return zip_path

def update_lambda_code():
    """Actualiza el código de la función Lambda"""
    print("🚀 Actualizando código Lambda...")
    
    # Crear ZIP
    zip_path = create_lambda_zip()
    
    # Actualizar función
    cmd = f"aws lambda update-function-code --function-name dnoc-chatbot-handler --zip-file fileb://{zip_path} --region us-west-2"
    success, output = run_command(cmd)
    
    if success:
        print("✅ Código Lambda actualizado exitosamente")
        return True
    else:
        print(f"❌ Error actualizando Lambda: {output}")
        return False

def verify_lambda():
    """Verifica la configuración de Lambda"""
    print("🔍 Verificando configuración Lambda...")
    
    # Verificar última modificación
    cmd = "aws lambda get-function --function-name dnoc-chatbot-handler --region us-west-2 --query Configuration.LastModified --output text"
    success, last_modified = run_command(cmd)
    
    if success:
        print(f"📅 Última modificación: {last_modified}")
    
    # Verificar variables de entorno
    cmd = "aws lambda get-function-configuration --function-name dnoc-chatbot-handler --region us-west-2 --query Environment.Variables --output json"
    success, env_vars = run_command(cmd)
    
    if success:
        try:
            env_dict = json.loads(env_vars)
            print("🔧 Variables de entorno:")
            for key, value in env_dict.items():
                print(f"   {key}: {value}")
        except:
            print("⚠️ No se pudieron obtener variables de entorno")

def get_api_endpoint():
    """Obtiene el endpoint de API Gateway"""
    print("🌐 Obteniendo endpoint de API...")
    
    cmd = "aws cloudformation describe-stacks --stack-name dnoc-chatbot-stack --region us-west-2 --query \"Stacks[0].Outputs[?OutputKey=='APIEndpoint'].OutputValue\" --output text"
    success, endpoint = run_command(cmd)
    
    if success and endpoint != "None":
        print(f"✅ API Endpoint: {endpoint}")
        print(f"\n📋 Configura esta variable de entorno:")
        print(f"set API_ENDPOINT={endpoint}")
        return endpoint
    else:
        print("❌ No se pudo obtener el endpoint. Verifica que el stack esté desplegado.")
        return None

def main():
    print("🔧 Configurando función Lambda DNOC...")
    print("=" * 50)
    
    # 1. Actualizar código Lambda
    if update_lambda_code():
        # 2. Verificar configuración
        verify_lambda()
        
        # 3. Obtener endpoint
        endpoint = get_api_endpoint()
        
        if endpoint:
            print("\n🎉 Configuración completada!")
            print("\n📝 Próximos pasos:")
            print("1. Configura la variable de entorno mostrada arriba")
            print("2. Ejecuta: cd frontend && python app.py")
        else:
            print("\n⚠️ Configuración parcial completada")
            print("Verifica que el stack de CloudFormation esté desplegado")
    else:
        print("\n❌ Error en la configuración")

if __name__ == "__main__":
    main()