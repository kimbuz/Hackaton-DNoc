import boto3

def get_api_endpoint():
    """Obtiene el endpoint de la API desplegada"""
    
    cf = boto3.client('cloudformation')
    stack_name = 'dnoc-chatbot-stack'
    
    try:
        response = cf.describe_stacks(StackName=stack_name)
        outputs = response['Stacks'][0].get('Outputs', [])
        
        for output in outputs:
            if output['OutputKey'] == 'APIEndpoint':
                endpoint = output['OutputValue']
                print(f"✅ API Endpoint: {endpoint}")
                return endpoint
        
        print("❌ No se encontró el endpoint en los outputs")
        return None
        
    except Exception as e:
        print(f"❌ Error obteniendo endpoint: {e}")
        return None

if __name__ == "__main__":
    endpoint = get_api_endpoint()
    if endpoint:
        print(f"\nConfigura esta variable de entorno:")
        print(f"set API_ENDPOINT={endpoint}")
    else:
        print("Verifica que el stack esté desplegado correctamente")