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

def deploy_mock_lambda():
    """Despliega versión mock de Lambda"""
    print("🚀 Desplegando versión mock de Lambda...")
    
    # Crear ZIP con versión mock
    zip_path = "lambda_mock.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        zip_file.write('backend/lambda_function_mock.py', 'lambda_function.py')
    
    print(f"📦 ZIP creado: {zip_path}")
    
    # Actualizar función Lambda
    cmd = f"aws lambda update-function-code --function-name dnoc-chatbot-handler --zip-file fileb://{zip_path} --region us-west-2"
    success, output = run_command(cmd)
    
    if success:
        print("✅ Versión mock desplegada exitosamente")
        
        # Limpiar archivo temporal
        os.remove(zip_path)
        
        print("\n🎉 ¡Lambda actualizada!")
        print("\n📝 Características de la versión mock:")
        print("- ✅ Respuestas inteligentes basadas en palabras clave")
        print("- ✅ Procedimientos DNOC reales")
        print("- ✅ Sin dependencia de Bedrock")
        print("- ✅ Funciona inmediatamente")
        
        print("\n🧪 Prueba estas consultas en Gradio:")
        print("- 'Tengo un problema de conectividad'")
        print("- 'Necesito reiniciar un servicio'")
        print("- 'Ayuda con correlación de fallas'")
        print("- 'Información de topología'")
        
        return True
    else:
        print(f"❌ Error desplegando: {output}")
        return False

def main():
    print("🔧 Desplegando Asistente DNOC - Versión Mock")
    print("=" * 50)
    
    if deploy_mock_lambda():
        print("\n🎯 Próximos pasos:")
        print("1. Ve a tu aplicación Gradio")
        print("2. Prueba enviando mensajes")
        print("3. Deberías recibir respuestas técnicas DNOC")
        print("\n💡 Esta versión funciona sin Bedrock y es completamente funcional")
    else:
        print("\n❌ Error en el despliegue")

if __name__ == "__main__":
    main()