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

def check_available_models():
    """Lista todos los modelos disponibles"""
    print("🔍 Verificando modelos disponibles en us-west-2...")
    
    cmd = "aws bedrock list-foundation-models --region us-west-2 --output json"
    success, output = run_command(cmd)
    
    if success:
        try:
            models = json.loads(output)
            claude_models = []
            
            print("📋 Modelos Claude disponibles:")
            for model in models['modelSummaries']:
                model_id = model['modelId']
                if 'claude' in model_id.lower():
                    claude_models.append(model_id)
                    print(f"   ✅ {model_id}")
            
            if claude_models:
                print(f"\n🎯 Modelos Claude encontrados: {len(claude_models)}")
                
                # Buscar específicamente Opus 4
                opus_models = [m for m in claude_models if 'opus-4' in m]
                if opus_models:
                    print(f"\n🚀 Modelos Opus 4 disponibles:")
                    for model in opus_models:
                        print(f"   🎯 {model}")
                    return opus_models[0]  # Retornar el primero
                else:
                    print("\n⚠️ No se encontró Claude Opus 4")
                    print("📋 Usa uno de estos modelos disponibles:")
                    for model in claude_models[:3]:  # Mostrar primeros 3
                        print(f"   - {model}")
                    return claude_models[0] if claude_models else None
            else:
                print("❌ No se encontraron modelos Claude")
                return None
                
        except json.JSONDecodeError:
            print(f"❌ Error parseando respuesta: {output}")
            return None
    else:
        print(f"❌ Error listando modelos: {output}")
        return None

def main():
    print("🔍 Verificando modelos Claude disponibles")
    print("=" * 50)
    
    correct_model = check_available_models()
    
    if correct_model:
        print(f"\n✅ Modelo recomendado: {correct_model}")
        print(f"\n🔧 Actualiza agent_config.py con:")
        print(f"'foundationModel': '{correct_model}',")
    else:
        print("\n❌ No se pudieron obtener modelos disponibles")
        print("Verifica que Bedrock esté habilitado en us-west-2")

if __name__ == "__main__":
    main()