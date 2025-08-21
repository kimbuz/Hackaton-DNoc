import boto3
from datetime import datetime, timedelta

def check_lambda_logs():
    """Verifica los logs de CloudWatch de la función Lambda"""
    
    logs_client = boto3.client('logs')
    
    # Nombre del log group de Lambda
    log_group_name = '/aws/lambda/dnoc-chatbot-handler'
    
    try:
        # Obtener logs de los últimos 10 minutos
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=10)
        
        response = logs_client.filter_log_events(
            logGroupName=log_group_name,
            startTime=int(start_time.timestamp() * 1000),
            endTime=int(end_time.timestamp() * 1000)
        )
        
        print(f"📋 Logs de Lambda (últimos 10 minutos):")
        print("=" * 60)
        
        for event in response['events']:
            timestamp = datetime.fromtimestamp(event['timestamp'] / 1000)
            message = event['message'].strip()
            print(f"[{timestamp.strftime('%H:%M:%S')}] {message}")
        
        if not response['events']:
            print("No hay logs recientes. La función puede no haberse ejecutado.")
            
    except Exception as e:
        print(f"❌ Error obteniendo logs: {e}")
        print("Verifica que el log group existe y tienes permisos")

if __name__ == "__main__":
    check_lambda_logs()