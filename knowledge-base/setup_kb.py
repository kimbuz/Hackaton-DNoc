import boto3
import json
import time

# Clientes AWS
bedrock_agent = boto3.client('bedrock-agent')
s3 = boto3.client('s3')
opensearch = boto3.client('opensearchserverless')

def create_s3_bucket(bucket_name):
    """Crea bucket S3 para documentos"""
    try:
        # Obtener región actual
        region = boto3.Session().region_name or 'us-west-2'
        
        if region == 'us-west-2':
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        print(f"Bucket S3 creado: {bucket_name}")
        return True
    except Exception as e:
        if 'BucketAlreadyExists' in str(e) or 'BucketAlreadyOwnedByYou' in str(e):
            print(f"Bucket ya existe: {bucket_name}")
            return True
        print(f"Error creando bucket: {e}")
        return False

def create_opensearch_collection():
    """Crea colección OpenSearch Serverless"""
    
    collection_name = "dnoc-knowledge-base"
    
    try:
        # Crear política de seguridad de encriptación
        try:
            opensearch.create_security_policy(
                name=f"{collection_name}-encryption",
                type='encryption',
                policy=json.dumps({
                    "Rules": [
                        {
                            "ResourceType": "collection",
                            "Resource": [f"collection/{collection_name}"]
                        }
                    ],
                    "AWSOwnedKey": True
                })
            )
            print("Política de encriptación creada")
        except Exception as policy_error:
            if 'ConflictException' not in str(policy_error):
                print(f"Advertencia política encriptación: {policy_error}")
        
        # Crear política de acceso de red
        try:
            opensearch.create_security_policy(
                name=f"{collection_name}-network",
                type='network',
                policy=json.dumps([
                    {
                        "Rules": [
                            {
                                "ResourceType": "collection",
                                "Resource": [f"collection/{collection_name}"]
                            }
                        ],
                        "AllowFromPublic": True
                    }
                ])
            )
            print("Política de red creada")
        except Exception as policy_error:
            if 'ConflictException' not in str(policy_error):
                print(f"Advertencia política red: {policy_error}")
        
        # Crear política de acceso de datos
        session = boto3.Session()
        sts = boto3.client('sts')
        account_id = sts.get_caller_identity()['Account']
        
        try:
            opensearch.create_access_policy(
                name=f"{collection_name}-access",
                type='data',
                policy=json.dumps([
                    {
                        "Rules": [
                            {
                                "ResourceType": "collection",
                                "Resource": [f"collection/{collection_name}"],
                                "Permission": [
                                    "aoss:CreateCollectionItems",
                                    "aoss:DeleteCollectionItems",
                                    "aoss:UpdateCollectionItems",
                                    "aoss:DescribeCollectionItems"
                                ]
                            },
                            {
                                "ResourceType": "index",
                                "Resource": [f"index/{collection_name}/*"],
                                "Permission": [
                                    "aoss:CreateIndex",
                                    "aoss:DeleteIndex",
                                    "aoss:UpdateIndex",
                                    "aoss:DescribeIndex",
                                    "aoss:ReadDocument",
                                    "aoss:WriteDocument"
                                ]
                            }
                        ],
                        "Principal": [
                            f"arn:aws:iam::{account_id}:role/service-role/AmazonBedrockExecutionRoleForKnowledgeBase_kb"
                        ]
                    }
                ])
            )
            print("Política de acceso de datos creada")
        except Exception as policy_error:
            if 'ConflictException' not in str(policy_error):
                print(f"Advertencia política acceso: {policy_error}")
        
        # Esperar un momento para que las políticas se propaguen
        import time
        time.sleep(5)
        
        # Crear colección
        response = opensearch.create_collection(
            name=collection_name,
            type='VECTORSEARCH',
            description='Colección para base de conocimiento DNOC'
        )
        print(f"Colección OpenSearch creada: {collection_name}")
        
        # Esperar a que la colección esté activa
        print("Esperando que la colección esté activa...")
        time.sleep(30)
        
        return collection_name
    except Exception as e:
        if 'ConflictException' in str(e):
            print(f"Colección ya existe: {collection_name}")
            return collection_name
        print(f"Error creando colección OpenSearch: {e}")
        return None

def create_knowledge_base(bucket_name, collection_name):
    """Crea la base de conocimiento en Bedrock"""
    
    # Obtener región y account ID
    session = boto3.Session()
    region = session.region_name or 'us-west-2'
    sts = boto3.client('sts')
    account_id = sts.get_caller_identity()['Account']
    
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
        'storageConfiguration': {
            'type': 'OPENSEARCH_SERVERLESS',
            'opensearchServerlessConfiguration': {
                'collectionArn': f'arn:aws:aoss:{region}:{account_id}:collection/{collection_name}',
                'vectorIndexName': 'dnoc-index',
                'fieldMapping': {
                    'vectorField': 'vector',
                    'textField': 'text',
                    'metadataField': 'metadata'
                }
            }
        }
    }
    
    try:
        response = bedrock_agent.create_knowledge_base(**kb_config)
        kb_id = response['knowledgeBase']['knowledgeBaseId']
        print(f"Base de conocimiento creada: {kb_id}")
        return kb_id
    except Exception as e:
        print(f"Error creando base de conocimiento: {e}")
        print(f"Detalles del error: {str(e)}")
        return None

def create_data_source(kb_id, bucket_name):
    """Crea fuente de datos S3 para la base de conocimiento"""
    
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
    
    try:
        response = bedrock_agent.create_data_source(**data_source_config)
        ds_id = response['dataSource']['dataSourceId']
        print(f"Fuente de datos creada: {ds_id}")
        return ds_id
    except Exception as e:
        print(f"Error creando fuente de datos: {e}")
        return None

def upload_sample_documents(bucket_name):
    """Sube documentos de ejemplo al bucket S3"""
    
    # Documento de ejemplo
    sample_doc = """
# Procedimientos DNOC - Resolución de Incidentes

## Fallas de Conectividad de Red

### Síntomas
- Pérdida de conectividad
- Timeouts en servicios
- Alertas de Fault Manager

### Procedimiento
1. Verificar estado de interfaces
2. Revisar logs de equipos
3. Validar topología de red
4. Ejecutar diagnósticos
5. Aplicar solución según tipo de falla

## Reinicio de Servicios

### Cuándo aplicar
- Servicios no responden
- Memoria alta en procesos
- Errores de aplicación

### Pasos
1. Identificar servicio afectado
2. Verificar dependencias
3. Ejecutar reinicio controlado
4. Validar funcionamiento
5. Monitorear estabilidad

## Correlación de Fallas

### Herramientas
- Fault Manager APIs
- Sistema de correlación basado en reglas
- Modelos predictivos

### Proceso
1. Recopilar eventos
2. Aplicar reglas de correlación
3. Identificar causa raíz
4. Generar recomendaciones
5. Ejecutar acciones correctivas
    """
    
    try:
        s3.put_object(
            Bucket=bucket_name,
            Key='documents/procedimientos-dnoc.txt',
            Body=sample_doc.encode('utf-8'),
            ContentType='text/plain'
        )
        print("Documento de ejemplo subido")
        return True
    except Exception as e:
        print(f"Error subiendo documento: {e}")
        return False

def sync_knowledge_base(kb_id, ds_id):
    """Sincroniza la base de conocimiento"""
    
    try:
        response = bedrock_agent.start_ingestion_job(
            knowledgeBaseId=kb_id,
            dataSourceId=ds_id
        )
        job_id = response['ingestionJob']['ingestionJobId']
        print(f"Sincronización iniciada: {job_id}")
        return job_id
    except Exception as e:
        print(f"Error iniciando sincronización: {e}")
        return None

if __name__ == "__main__":
    bucket_name = "dnoc-knowledge-base-docs"
    
    print("Configurando base de conocimiento DNOC...")
    
    # 1. Crear bucket S3
    create_s3_bucket(bucket_name)
    
    # 2. Subir documentos de ejemplo
    upload_sample_documents(bucket_name)
    
    # 3. Crear colección OpenSearch
    collection_name = create_opensearch_collection()
    
    if collection_name:
        # 4. Crear base de conocimiento
        kb_id = create_knowledge_base(bucket_name, collection_name)
        
        if kb_id:
            # 5. Crear fuente de datos
            ds_id = create_data_source(kb_id, bucket_name)
            
            if ds_id:
                # 6. Sincronizar
                job_id = sync_knowledge_base(kb_id, ds_id)
                
                print(f"\nConfiguración completada:")
                print(f"Knowledge Base ID: {kb_id}")
                print(f"Data Source ID: {ds_id}")
                print(f"Sync Job ID: {job_id}")
            else:
                print("Error en la configuración de fuente de datos")
        else:
            print("Error en la configuración de base de conocimiento")
    else:
        print("Error en la configuración de OpenSearch")