import subprocess
import json

def get_stack_outputs():
    """Obtiene outputs del stack usando AWS CLI"""
    
    try:
        # Usar AWS CLI para obtener outputs del stack
        cmd = [
            'aws', 'cloudformation', 'describe-stacks',
            '--stack-name', 'dnoc-chatbot-stack',
            '--query', 'Stacks[0].Outputs',
            '--output', 'json'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            outputs = json.loads(result.stdout)
            
            print("📋 Outputs del Stack:")
            print("=" * 50)
            
            api_endpoint = None
            for output in outputs:
                key = output['OutputKey']
                value = output['OutputValue']
                print(f"{key}: {value}")
                
                if key == 'APIEndpoint':
                    api_endpoint = value
            
            if api_endpoint:
                print(f"\n✅ Configura esta variable:")
                print(f"set API_ENDPOINT={api_endpoint}")
                return api_endpoint
            else:
                print("\n❌ No se encontró APIEndpoint")
                return None
        else:
            print(f"❌ Error ejecutando AWS CLI: {result.stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    get_stack_outputs()