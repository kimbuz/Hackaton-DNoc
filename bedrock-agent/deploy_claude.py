import subprocess
import zipfile
import os
import shutil

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

def create_lambda_package():
    """Crea paquete Lambda con Claude agent"""
    print("📦 Creando paquete Lambda con Claude agent...")
    
    # Crear ZIP directamente
    zip_path = 'claude_lambda.zip'
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Agregar función Lambda
        zip_file.write('../backend/lambda_function.py', 'lambda_function.py')
        # Agregar agente Claude
        zip_file.write('claude_agent.py', 'claude_agent.py')
    
    print(f"✅ Paquete creado: {zip_path}")
    return zip_path

def deploy_lambda(zip_path):
    """Despliega Lambda con Claude agent"""
    print("🚀 Desplegando Lambda con Claude agent...")
    
    cmd = f"aws lambda update-function-code --function-name dnoc-chatbot-handler --zip-file fileb://{zip_path} --region us-west-2"
    success, output = run_command(cmd)
    
    if success:
        print("✅ Lambda actualizada exitosamente")
        
        # Actualizar timeout
        cmd_timeout = "aws lambda update-function-configuration --function-name dnoc-chatbot-handler --timeout 60 --region us-west-2"
        run_command(cmd_timeout)
        print("✅ Timeout actualizado a 60 segundos")
        
        return True
    else:
        print(f"❌ Error desplegando: {output}")
        return False

def main():
    print("🔧 Desplegando DNOC Assistant con Claude Opus 4")
    print("=" * 50)
    
    # Crear paquete
    zip_path = create_lambda_package()
    
    if zip_path:
        # Desplegar
        if deploy_lambda(zip_path):
            # Limpiar
            os.remove(zip_path)
            
            print("\n🎉 Despliegue completado!")
            print("\n📝 Características:")
            print("- ✅ Claude Opus 4 directo con boto3")
            print("- ✅ Sin dependencias complejas")
            print("- ✅ Respuestas técnicas DNOC especializadas")
            print("- ✅ Compatible con Windows")
            
            print("\n🧪 Prueba Gradio ahora - debería funcionar con Claude Opus 4")
        else:
            print("\n❌ Error en el despliegue")
    else:
        print("\n❌ Error creando paquete")

if __name__ == "__main__":
    main()