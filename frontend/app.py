import gradio as gr
import requests
import json
import os
from datetime import datetime

# Configuración
API_ENDPOINT = os.getenv('API_ENDPOINT', 'https://your-api-gateway-url.amazonaws.com/prod/chat')

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
            return result.get('response', 'Error: Respuesta vacía')
        else:
            return f"Error: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"Error de conexión: {str(e)}"

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
    submit_btn.click(chat_with_agent, [msg, chatbot], [chatbot])
    msg.submit(chat_with_agent, [msg, chatbot], [chatbot])
    clear_btn.click(clear_chat, outputs=[chatbot])
    
    # Limpiar input después de enviar
    submit_btn.click(lambda: "", outputs=[msg])
    msg.submit(lambda: "", outputs=[msg])

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )