import boto3
import json

def create_bedrock_kb_role():
    """Crea el rol IAM necesario para Bedrock Knowledge Base"""
    
    iam = boto3.client('iam')
    
    # Política de confianza
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # Política de permisos
    permissions_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::dnoc-knowledge-base-docs",
                    "arn:aws:s3:::dnoc-knowledge-base-docs/*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "aoss:APIAccessAll"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel"
                ],
                "Resource": "*"
            }
        ]
    }
    
    role_name = "AmazonBedrockExecutionRoleForKnowledgeBase_kb"
    
    # Crear path service-role si no existe
    try:
        iam.create_role(
            Path='/service-role/',
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Rol para Bedrock Knowledge Base DNOC'
        )
        print(f"Rol IAM creado: {role_name}")
        
        # Adjuntar política
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName='BedrockKnowledgeBasePolicy',
            PolicyDocument=json.dumps(permissions_policy)
        )
        print("Política adjuntada al rol")
        
        return True
        
    except Exception as e:
        if 'EntityAlreadyExists' in str(e):
            print(f"Rol ya existe: {role_name}")
            return True
        print(f"Error creando rol: {e}")
        return False

def create_bedrock_kb_role_fallback():
    """Versión alternativa sin path service-role"""
    
    iam = boto3.client('iam')
    
    # Política de confianza
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    # Política de permisos
    permissions_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    "arn:aws:s3:::dnoc-knowledge-base-docs",
                    "arn:aws:s3:::dnoc-knowledge-base-docs/*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "aoss:APIAccessAll"
                ],
                "Resource": "*"
            },
            {
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel"
                ],
                "Resource": "*"
            }
        ]
    }
    
    role_name = "BedrockKnowledgeBaseRole"
    
    try:
        # Crear rol alternativo
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Rol para Bedrock Knowledge Base DNOC'
        )
        print(f"Rol IAM alternativo creado: {role_name}")
        
        # Adjuntar política
        iam.put_role_policy(
            RoleName=role_name,
            PolicyName='BedrockKnowledgeBasePolicy',
            PolicyDocument=json.dumps(permissions_policy)
        )
        print("Política adjuntada al rol alternativo")
        
        return role_name
        
    except Exception as e:
        if 'EntityAlreadyExists' in str(e):
            print(f"Rol alternativo ya existe: {role_name}")
            return role_name
        print(f"Error creando rol alternativo: {e}")
        return None

if __name__ == "__main__":
    # Intentar crear rol principal
    success = create_bedrock_kb_role()
    
    if not success:
        print("Intentando crear rol alternativo...")
        alt_role = create_bedrock_kb_role_fallback()
        if alt_role:
            print(f"Usar este ARN en setup_kb.py: arn:aws:iam::ACCOUNT:{alt_role}")
        else:
            print("Error: No se pudo crear ningún rol IAM")