import boto3
import json
import zipfile
import os
import time

# Cliente CloudFormation
cf = boto3.client('cloudformation')
lambda_client = boto3.client('lambda')

def create_lambda_package():
    """Crea el paquete ZIP para Lambda"""
    
    zip_path = 'lambda-deployment.zip'
    
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        # Agregar función Lambda
        zip_file.write('../backend/lambda_function.py', 'lambda_function.py')
    
    print(f"Paquete Lambda creado: {zip_path}")
    return zip_path

def deploy_infrastructure(agent_id, agent_alias_id):
    """Despliega la infraestructura usando CloudFormation"""
    
    stack_name = 'dnoc-chatbot-stack'
    
    with open('cloudformation.yaml', 'r') as f:
        template_body = f.read()
    
    parameters = [
        {
            'ParameterKey': 'AgentId',
            'ParameterValue': agent_id
        },
        {
            'ParameterKey': 'AgentAliasId',
            'ParameterValue': agent_alias_id
        }
    ]
    
    try:
        # Crear stack
        response = cf.create_stack(
            StackName=stack_name,
            TemplateBody=template_body,
            Parameters=parameters,
            Capabilities=['CAPABILITY_NAMED_IAM']
        )
        
        print(f"Stack creado: {stack_name}")
        
        # Esperar a que se complete
        waiter = cf.get_waiter('stack_create_complete')
        print("Esperando que se complete el despliegue...")
        waiter.wait(StackName=stack_name)
        
        # Obtener outputs
        stack_info = cf.describe_stacks(StackName=stack_name)
        outputs = stack_info['Stacks'][0].get('Outputs', [])
        
        result = {}
        for output in outputs:
            result[output['OutputKey']] = output['OutputValue']
        
        return result
        
    except Exception as e:
        print(f"Error desplegando infraestructura: {e}")
        return None

def update_lambda_code(function_name, zip_path):
    """Actualiza el código de la función Lambda"""
    
    try:
        with open(zip_path, 'rb') as zip_file:
            lambda_client.update_function_code(
                FunctionName=function_name,
                ZipFile=zip_file.read()
            )
        
        print(f"Código Lambda actualizado: {function_name}")
        return True
        
    except Exception as e:
        print(f"Error actualizando Lambda: {e}")
        return False

if __name__ == "__main__":
    # Solicitar IDs del agente
    agent_id = input("Ingresa el AGENT_ID: ")
    agent_alias_id = input("Ingresa el AGENT_ALIAS_ID: ")
    
    if not agent_id or not agent_alias_id:
        print("Error: Se requieren ambos IDs del agente")
        exit(1)
    
    print("Iniciando despliegue...")
    
    # 1. Crear paquete Lambda
    zip_path = create_lambda_package()
    
    # 2. Desplegar infraestructura
    outputs = deploy_infrastructure(agent_id, agent_alias_id)
    
    if outputs:
        # 3. Actualizar código Lambda
        function_name = outputs.get('LambdaFunctionName')
        if function_name:
            update_lambda_code(function_name, zip_path)
        
        # 4. Mostrar resultados
        print("\n✅ Despliegue completado!")
        print(f"API Endpoint: {outputs.get('APIEndpoint')}")
        print(f"Lambda Function: {outputs.get('LambdaFunctionName')}")
        
        # 5. Limpiar archivos temporales
        os.remove(zip_path)
        
    else:
        print("❌ Error en el despliegue")