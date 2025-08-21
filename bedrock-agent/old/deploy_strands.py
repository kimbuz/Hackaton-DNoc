import subprocess
import zipfile
import os

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
    """Crea paquete Lambda con Strands"""
    print("📦 Creando paquete Lambda con Strands...")
    
    # Crear directorio temporal
    os.makedirs('lambda_package', exist_ok=True)
    
    # Instalar Strands en directorio temporal
    print("📥 Instalando Strands...")
    cmd = "pip install strands -t lambda_package/"
    success, output = run_command(cmd)
    
    if not success:
        print(f"❌ Error instalando Strands: {output}")
        return None
    
    # Copiar archivos del proyecto
    import shutil
    shutil.copy('../backend/lambda_function.py', 'lambda_package/')
    shutil.copy('strands_agent.py', 'lambda_package/')
    
    # Crear ZIP
    zip_path = 'strands_lambda.zip'
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, dirs, files in os.walk('lambda_package'):
            for file in files:
                file_path = os.path.join(root, file)
                arc_path = os.path.relpath(file_path, 'lambda_package')
                zip_file.write(file_path, arc_path)
    
    # Limpiar directorio temporal
    shutil.rmtree('lambda_package')
    
    print(f"✅ Paquete creado: {zip_path}")
    return zip_path

def deploy_lambda(zip_path):
    """Despliega Lambda con Strands"""
    print("🚀 Desplegando Lambda con Strands...")
    
    cmd = f"aws lambda update-function-code --function-name dnoc-chatbot-handler --zip-file fileb://{zip_path} --region us-west-2"
    success, output = run_command(cmd)
    
    if success:
        print("✅ Lambda actualizada exitosamente")
        
        # Actualizar timeout (Strands puede necesitar más tiempo)
        cmd_timeout = "aws lambda update-function-configuration --function-name dnoc-chatbot-handler --timeout 60 --region us-west-2"
        run_command(cmd_timeout)
        print("✅ Timeout actualizado a 60 segundos")
        
        return True
    else:
        print(f"❌ Error desplegando: {output}")
        return False

def main():
    print("🔧 Desplegando DNOC Assistant con Strands + Claude Opus 4")
    print("=" * 60)
    
    # Crear paquete
    zip_path = create_lambda_package()
    
    if zip_path:
        # Desplegar
        if deploy_lambda(zip_path):
            # Limpiar
            os.remove(zip_path)
            
            print("\n🎉 Despliegue completado!")
            print("\n📝 Características:")
            print("- ✅ Strands Agent con Claude Opus 4")
            print("- ✅ Respuestas técnicas DNOC especializadas")
            print("- ✅ Sin dependencia de Bedrock Agents")
            print("- ✅ Timeout extendido para mejor rendimiento")
            
            print("\n🧪 Prueba Gradio ahora - debería funcionar con Claude Opus 4")
        else:
            print("\n❌ Error en el despliegue")
    else:
        print("\n❌ Error creando paquete")

if __name__ == "__main__":
    main()