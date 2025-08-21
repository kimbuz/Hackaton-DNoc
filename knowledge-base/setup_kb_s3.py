import boto3
import json

def create_kb_with_s3_vector():
    """Crea Knowledge Base usando S3 para almacenamiento vectorial"""
    
    bedrock_agent = boto3.client('bedrock-agent')
    
    # Obtener región y account ID
    session = boto3.Session()
    region = session.region_name or 'us-east-1'
    sts = boto3.client('sts')
    account_id = sts.get_caller_identity()['Account']
    
    bucket_name = "dnoc-knowledge-base-docs"
    
    kb_config = {
        'name': 'dnoc-technical-kb',
        'description': 'Base de conocimiento técnico para DNOC',
        'roleArn': f'arn:aws:iam::{account_id}:role/service-role/AmazonBedrockExecutionRoleForKnowledgeBase_kb',
        'knowledgeBaseConfiguration': {
            'type': 'VECTOR',
            'vectorKnowledgeBaseConfiguration': {
                'embeddingModelArn': f'arn:aws:bedrock:{region}::foundation-model/amazon.titan-embed-text-v1'
            }
        },
# Sin storageConfiguration - Bedrock creará automáticamente
    }
    
    try:
        response = bedrock_agent.create_knowledge_base(**kb_config)
        kb_id = response['knowledgeBase']['knowledgeBaseId']
        print(f"✅ Base de conocimiento creada: {kb_id}")
        
        # Crear fuente de datos S3
        data_source_config = {
            'knowledgeBaseId': kb_id,
            'name': 'dnoc-documents',
            'description': 'Documentos técnicos DNOC',
            'dataSourceConfiguration': {
                'type': 'S3',
                's3Configuration': {
                    'bucketArn': f'arn:aws:s3:::{bucket_name}',
                    'inclusionPrefixes': ['documents/']
                }
            }
        }
        
        ds_response = bedrock_agent.create_data_source(**data_source_config)
        ds_id = ds_response['dataSource']['dataSourceId']
        print(f"✅ Fuente de datos creada: {ds_id}")
        
        # Iniciar sincronización
        sync_response = bedrock_agent.start_ingestion_job(
            knowledgeBaseId=kb_id,
            dataSourceId=ds_id
        )
        job_id = sync_response['ingestionJob']['ingestionJobId']
        print(f"✅ Sincronización iniciada: {job_id}")
        
        print(f"\n🎉 Configuración completada:")
        print(f"Knowledge Base ID: {kb_id}")
        
        return kb_id
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    create_kb_with_s3_vector()