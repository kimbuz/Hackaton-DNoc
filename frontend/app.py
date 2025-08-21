import gradio as gr
import requests
import json
import os
from datetime import datetime

# Configuración
# API_ENDPOINT = os.getenv('API_ENDPOINT', 'https://nk3mn7a324.execute-api.us-west-2.amazonaws.com/prod/chat')
API_ENDPOINT='https://nk3mn7a324.execute-api.us-west-2.amazonaws.com/prod/chat'
print(f"Usando API Endpoint: {API_ENDPOINT}")

def chat_with_agent(message, history):
    """Envía mensaje al agente de Bedrock y retorna respuesta"""
    try:
        # Preparar payload
        payload = {
            "message": message,
            "session_id": "dnoc-session"
        }
        
        # Llamar a la API
        response = requests.post(
            API_ENDPOINT,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            bot_response = result.get('response', 'Error: Respuesta vacía')
        else:
            bot_response = f"Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        bot_response = f"Error de conexión: {str(e)}\n\n⚠️ Verifica que API_ENDPOINT esté configurado correctamente"
    
    # Agregar mensaje a historial en formato correcto
    history.append([message, bot_response])
    return history, ""

def clear_chat():
    """Limpia el historial de chat"""
    return []

# Crear interfaz Gradio
with gr.Blocks(title="DNOC Assistant", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 DNOC Assistant - Chatbot Técnico")
    gr.Markdown("Asistente especializado en resolución de incidentes y consultas técnicas DNOC")
    
    chatbot = gr.Chatbot(
        height=500,
        placeholder="Hola, soy tu asistente DNOC. ¿En qué puedo ayudarte hoy?"
    )
    
    with gr.Row():
        msg = gr.Textbox(
            placeholder="Escribe tu consulta técnica aquí...",
            container=False,
            scale=4
        )
        submit_btn = gr.Button("Enviar", scale=1, variant="primary")
        clear_btn = gr.Button("Limpiar", scale=1)
    
    # Ejemplos de consultas
    gr.Examples(
        examples=[
            "¿Cómo resolver un problema de conectividad en la red?",
            "Explícame el procedimiento para reiniciar un servicio",
            "¿Qué hacer cuando hay una falla en el sistema de correlación?",
            "Necesito información sobre la topología de equipos"
        ],
        inputs=msg
    )
    
    # Eventos
    submit_btn.click(chat_with_agent, [msg, chatbot], [chatbot, msg])
    msg.submit(chat_with_agent, [msg, chatbot], [chatbot, msg])
    clear_btn.click(clear_chat, outputs=[chatbot])

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )