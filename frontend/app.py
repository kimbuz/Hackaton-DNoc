import gradio as gr
import requests
import json
import os
from datetime import datetime
import logging
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_GATEWAY_URL = os.getenv('API_GATEWAY_URL', '')
API_KEY = os.getenv('API_KEY', '')  # Optional API key for security

class DNOCChatbot:
    def __init__(self):
        self.session_id = None
        
    def call_lambda_backend(self, message, history):
        """Call Lambda function via API Gateway"""
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            # Add API key if configured
            if API_KEY:
                headers["x-api-key"] = API_KEY
            
            payload = {
                "message": message,
                "history": history,
                "session_id": self.session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Calling Lambda with message: {message[:50]}...")
            
            response = requests.post(
                f"{API_GATEWAY_URL}/chat",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response received")
            else:
                logger.error(f"API call failed: {response.status_code} - {response.text}")
                return f"Error: API call failed with status {response.status_code}"
                
        except requests.exceptions.Timeout:
            return "Error: Request timed out. Please try again."
        except requests.exceptions.ConnectionError:
            return "Error: Unable to connect to backend service."
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return f"Error: {str(e)}"
    
    def respond(self, message, chat_history):
        """Handle chat response"""
        if not message.strip():
            return chat_history, ""
        
        # Get response from Lambda backend
        bot_response = self.call_lambda_backend(message, chat_history)
        
        # Update chat history
        chat_history.append((message, bot_response))
        return chat_history, ""
    
    def clear_chat(self):
        """Clear chat history"""
        self.session_id = None
        return []

# Initialize chatbot
dnoc_bot = DNOCChatbot()

# Create Gradio interface
def create_interface():
    # Custom Telecom Argentina formal CSS
    telecom_css = """
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto:wght@300;400;500;700&display=swap');
        
        :root {
            --telecom-blue: #0066cc;
            --telecom-dark-blue: #003d7a;
            --telecom-light-blue: #4d94ff;
            --telecom-gray: #6c757d;
            --telecom-light-gray: #f8f9fa;
            --telecom-dark-gray: #343a40;
            --telecom-white: #ffffff;
            --telecom-accent: #28a745;
            --telecom-warning: #ffc107;
            --telecom-danger: #dc3545;
            --card-shadow: 0 2px 10px rgba(0, 102, 204, 0.1);
            --border-radius: 8px;
        }
        
        /* Main container */
        .gradio-container {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%) !important;
            font-family: 'Inter', sans-serif !important;
            color: var(--telecom-dark-gray) !important;
            min-height: 100vh;
            position: relative;
            padding: 20px !important;
        }
        
        /* Professional text colors */
        * {
            color: var(--telecom-dark-gray) !important;
        }
        
        /* Override gray text to dark gray for readability */
        [style*="color: rgb(31, 41, 55)"],
        [style*="color:rgb(31,41,55)"],
        .text-gray-700,
        .text-slate-700 {
            color: var(--telecom-dark-gray) !important;
        }
        
        /* Headers with Telecom blue */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', sans-serif !important;
            color: var(--telecom-blue) !important;
            font-weight: 600 !important;
            margin: 20px 0 !important;
        }
        
        /* Main title styling */
        .gradio-container h1:first-of-type {
            font-size: 2.2rem !important;
            color: var(--telecom-dark-blue) !important;
            text-align: center !important;
            font-weight: 700 !important;
            margin-bottom: 10px !important;
        }
        
        /* Professional card styling */
        .professional-card {
            background: var(--telecom-white) !important;
            border: 1px solid #dee2e6 !important;
            border-radius: var(--border-radius) !important;
            box-shadow: var(--card-shadow) !important;
            padding: 20px !important;
            margin: 15px 0 !important;
        }
        
        /* Chatbot container */
        .chatbot {
            background: var(--telecom-white) !important;
            border: 1px solid #dee2e6 !important;
            border-radius: var(--border-radius) !important;
            box-shadow: var(--card-shadow) !important;
        }
        
        /* Chat messages */
        .chatbot .message-wrap,
        .chatbot .message,
        .chatbot .message-content {
            color: var(--telecom-dark-gray) !important;
            font-family: 'Inter', sans-serif !important;
            line-height: 1.6 !important;
        }
        
        /* User messages */
        .chatbot .message-wrap.user {
            background: rgba(0, 102, 204, 0.05) !important;
            border-left: 4px solid var(--telecom-blue) !important;
            margin: 8px 0 !important;
            padding: 12px !important;
            border-radius: 0 var(--border-radius) var(--border-radius) 0 !important;
        }
        
        /* Bot messages */
        .chatbot .message-wrap.bot {
            background: rgba(108, 117, 125, 0.05) !important;
            border-left: 4px solid var(--telecom-gray) !important;
            margin: 8px 0 !important;
            padding: 12px !important;
            border-radius: 0 var(--border-radius) var(--border-radius) 0 !important;
        }
        
        /* Input textbox */
        .gradio-textbox input, .gradio-textbox textarea {
            background: var(--telecom-white) !important;
            border: 2px solid #dee2e6 !important;
            border-radius: var(--border-radius) !important;
            color: var(--telecom-dark-gray) !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 14px !important;
            padding: 12px 16px !important;
            transition: all 0.3s ease !important;
        }
        
        .gradio-textbox input:focus, .gradio-textbox textarea:focus {
            border-color: var(--telecom-blue) !important;
            box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1) !important;
            outline: none !important;
        }
        
        .gradio-textbox input::placeholder, .gradio-textbox textarea::placeholder {
            color: var(--telecom-gray) !important;
            font-style: normal !important;
        }
        
        /* Professional buttons */
        .gradio-button {
            background: var(--telecom-blue) !important;
            border: 1px solid var(--telecom-blue) !important;
            border-radius: var(--border-radius) !important;
            color: var(--telecom-white) !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            padding: 12px 24px !important;
            transition: all 0.3s ease !important;
            text-transform: none !important;
            letter-spacing: normal !important;
        }
        
        .gradio-button:hover {
            background: var(--telecom-dark-blue) !important;
            border-color: var(--telecom-dark-blue) !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3) !important;
        }
        
        /* Secondary buttons */
        .gradio-button.secondary {
            background: transparent !important;
            border-color: var(--telecom-gray) !important;
            color: var(--telecom-gray) !important;
        }
        
        .gradio-button.secondary:hover {
            background: var(--telecom-gray) !important;
            color: var(--telecom-white) !important;
            border-color: var(--telecom-gray) !important;
        }
        
        /* Example buttons */
        .example-btn {
            background: var(--telecom-light-gray) !important;
            border: 1px solid #dee2e6 !important;
            border-radius: var(--border-radius) !important;
            color: var(--telecom-dark-gray) !important;
            font-family: 'Inter', sans-serif !important;
            font-size: 13px !important;
            padding: 10px 15px !important;
            margin: 5px 0 !important;
            transition: all 0.3s ease !important;
            text-align: left !important;
            font-weight: 400 !important;
        }
        
        .example-btn:hover {
            background: var(--telecom-blue) !important;
            border-color: var(--telecom-blue) !important;
            color: var(--telecom-white) !important;
            transform: translateX(5px) !important;
        }
        
        /* Sidebar */
        .sidebar {
            background: var(--telecom-white) !important;
            border: 1px solid #dee2e6 !important;
            border-radius: var(--border-radius) !important;
            padding: 20px !important;
            box-shadow: var(--card-shadow) !important;
        }
        
        /* Status indicator */
        .status-indicator {
            background: var(--telecom-white) !important;
            border: 1px solid #dee2e6 !important;
            border-radius: var(--border-radius) !important;
            padding: 12px !important;
            text-align: center !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 500 !important;
            box-shadow: var(--card-shadow) !important;
            color: var(--telecom-dark-gray) !important;
        }
        
        /* Markdown content */
        .markdown {
            color: var(--telecom-dark-gray) !important;
            font-family: 'Inter', sans-serif !important;
            line-height: 1.7 !important;
        }
        
        .markdown h1, .markdown h2, .markdown h3 {
            color: var(--telecom-blue) !important;
            font-weight: 600 !important;
        }
        
        .markdown strong {
            color: var(--telecom-dark-blue) !important;
            font-weight: 600 !important;
        }
        
        .markdown em {
            color: var(--telecom-gray) !important;
            font-style: italic !important;
        }
        
        .markdown ul li {
            margin: 8px 0 !important;
        }
        
        .markdown ul li::marker {
            color: var(--telecom-blue) !important;
        }
        
        /* Professional header */
        .professional-header {
            background: var(--telecom-white) !important;
            border: 1px solid #dee2e6 !important;
            border-radius: var(--border-radius) !important;
            padding: 30px !important;
            box-shadow: var(--card-shadow) !important;
            text-align: center !important;
        }
        
        /* Professional footer */
        .professional-footer {
            background: var(--telecom-dark-blue) !important;
            color: var(--telecom-white) !important;
            border-radius: var(--border-radius) !important;
            padding: 20px !important;
            text-align: center !important;
        }
        
        .professional-footer * {
            color: var(--telecom-white) !important;
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--telecom-light-gray);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--telecom-blue);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--telecom-dark-blue);
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .gradio-container {
                padding: 10px !important;
            }
            
            h1 {
                font-size: 1.8rem !important;
            }
            
            .professional-card {
                padding: 15px !important;
            }
        }
    """
    
    with gr.Blocks(
        title="DNOC - Centro de Operaciones de Red",
        theme=gr.themes.Soft(),
        css=telecom_css,
        fill_width=True,
    ) as interface:
        
        # Header
        gr.Markdown("""
        # 🏢 DNOC - N.I.R.A.
        """, elem_classes=["professional-header"])
        
        # Chat interface
        with gr.Row():
            with gr.Column(scale=4):
                chatbot = gr.Chatbot(
                    value=[],
                    elem_id="chatbot",
                    bubble_full_width=True,
                    height=500,
                    show_copy_button=False,
                    elem_classes=["professional-card"]
                )
                
                with gr.Row():
                    msg = gr.Textbox(
                        placeholder="Describa su consulta técnica o incidente de red...",
                        container=False,
                        scale=8,
                        lines=3,
                        max_lines=3,
                        show_label=False,
                        interactive=True,
                        autofocus=True
                    )
                    with gr.Column(scale=1):
                        submit = gr.Button("Enviar", variant="primary", size="lg")
                        clear = gr.Button("Limpiar", variant="secondary")
            
            # Sidebar with examples
            with gr.Column(scale=1, elem_classes=["sidebar"]):
                gr.Markdown("### 💡 Consultas Frecuentes")
                
                examples = [
                    "Que es un servicio de WAG?",
                    "Hay algun problema en el WAG?"
                ]
                
                for example in examples:
                    example_btn = gr.Button(example, size="sm", variant="secondary", elem_classes=["example-btn"])
                    example_btn.click(
                        lambda x=example: x,
                        outputs=[msg]
                    )
        
        # Status indicator
        with gr.Row():
            status = gr.Markdown("🟢 **Estado del Sistema**: Operativo", elem_classes=["status-indicator"])
        
        # Event handlers
        def submit_message(message, history):
            if not message.strip():
                return history, "", "🔴 **Estado del Sistema**: Ingrese un mensaje"
            
            # Get response
            new_history, empty_msg = dnoc_bot.respond(message, history)
            
            return new_history, empty_msg, "🟢 **Estado del Sistema**: Operativo"
        
        # Enter key event
        msg.submit(
            submit_message,
            inputs=[msg, chatbot],
            outputs=[chatbot, msg, status]
        )

        # Button click event
        submit.click(
            submit_message,
            inputs=[msg, chatbot],
            outputs=[chatbot, msg, status]
        )

        clear.click(
            lambda: (dnoc_bot.clear_chat(), "🟢 **Estado del Sistema**: Conversación reiniciada"),
            outputs=[chatbot, status],
            queue=False
        )
        
        # Footer
        gr.Markdown("""
        **DNOC - Centro de Operaciones de Red** | Telecom Argentina  
        Powered by Amazon Bedrock | Versión 2.0  | © 2024 - Sistema de Asistencia Técnica Especializada
        """, elem_classes=["professional-footer"])
    
    return interface

if __name__ == "__main__":
    # Create and launch the interface
    app = create_interface()
    
    # Launch configuration
    app.launch(
        server_name="0.0.0.0",  # Allow external access
        server_port=7860,
        share=False,
        show_error=True,
        quiet=False
    )
