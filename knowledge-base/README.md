# Knowledge Base - DNOC Technical Documentation

Base de conocimiento que contiene documentación técnica para el asistente DNOC.

## Componentes

- **S3 Bucket**: Almacena documentos (PDFs, Word, texto)
- **OpenSearch Serverless**: Índice vectorial para búsquedas
- **Bedrock Knowledge Base**: Integración con el agente

## Configuración

```bash
python setup_kb.py
```

Este script:
1. Crea bucket S3 para documentos
2. Sube documentos de ejemplo
3. Configura OpenSearch Serverless
4. Crea la base de conocimiento en Bedrock
5. Configura fuente de datos S3
6. Inicia sincronización

## Documentos Soportados

- Procedimientos técnicos (.txt, .md)
- Manuales (.pdf, .docx)
- Documentación Confluence (exportada)
- Inventarios de topología (.json, .csv)
- Guías de resolución de problemas

## Estructura de Documentos en S3

```
bucket-name/
└── documents/
    ├── procedimientos/
    ├── manuales/
    ├── topologia/
    └── resoluciones/
```