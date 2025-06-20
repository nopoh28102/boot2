from flask import Flask, request, jsonify, render_template
import os
import requests
from dotenv import load_dotenv
from database import Database
from message_handler import MessageHandler
from admin import admin
from logger import Logger
from session_manager import SessionManager
from menu_manager import MenuManager
from analytics import Analytics
from ai_engine import AIEngine
from conversation_learner import ConversationLearner

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-12345")
app.register_blueprint(admin)

# Initialize components
db = Database()
session_manager = SessionManager()
logger = Logger()
menu_manager = MenuManager()
analytics = Analytics()
ai_engine = AIEngine()
conversation_learner = ConversationLearner()
message_handler = None  # Will be initialized after send_message function is defined

# Facebook Configuration
PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')

# Home page route
@app.route('/')
def home():
    return render_template('index.html')

def send_message(recipient_id, response):
    """Send message to user using Facebook Graph API"""
    endpoint = f"https://graph.facebook.com/v17.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    
    response_data = {
        "recipient": {"id": recipient_id},
        "message": response
    }
    
    requests.post(endpoint, json=response_data, params=params, headers=headers)

async def handle_text_message(sender_id, message_text):
    """Handle incoming text messages"""
    try:
        # First, check for learned responses
        learned_response = conversation_learner.get_learned_response(message_text)
        if learned_response and learned_response['confidence'] > 0.8:
            response_data = {"text": learned_response['text']}
            send_message(sender_id, response_data)
            analytics.log_interaction(sender_id, 'learned_response', message_text)
            return

        # Get session context
        session = session_manager.get_session(sender_id)
        context = session.context if session else None

        # Generate AI response
        ai_response = await ai_engine.generate_response(sender_id, message_text, context)
        
        if isinstance(ai_response, str):
            response_data = {"text": ai_response}
        else:
            response_data = ai_response

        send_message(sender_id, response_data)
        analytics.log_interaction(sender_id, 'ai_response', message_text)

    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        error_message = {"text": "عذراً، حدث خطأ. الرجاء المحاولة مرة أخرى."}
        send_message(sender_id, error_message)

def send_template_message(recipient_id, template_data):
    """Send a template message"""
    response = {
        "attachment": {
            "type": "template",
            "payload": template_data
        }
    }
    send_message(recipient_id, response)

def send_media_message(recipient_id, media_type, url):
    """Send media messages (image, audio, video, file)"""
    response = {
        "attachment": {
            "type": media_type,
            "payload": {
                "url": url
            }
        }
    }
    send_message(recipient_id, response)

@app.route('/feedback', methods=['POST'])
def handle_feedback():
    """Handle user feedback for responses"""
    try:
        data = request.get_json()
        conversation_id = data.get('conversation_id')
        feedback_score = data.get('score', 0)  # Score from -1 to 1
        
        if conversation_id:
            # Save feedback
            db.save_feedback(conversation_id, feedback_score)
            
            # Learn from positive feedback
            if feedback_score > 0:
                conversation_learner.learn_from_feedback(conversation_id, feedback_score)
            
            return jsonify({"status": "success"})
        
        return jsonify({"status": "error", "message": "Missing conversation_id"}), 400
    
    except Exception as e:
        logger.error(f"Error handling feedback: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Handle the webhook verification from Facebook"""
    if request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge') or ''
    return 'Invalid verification token'

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming messages from Facebook"""
    data = request.get_json()
    
    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                sender_id = messaging_event['sender']['id']
                
                # Get or create session for user
                session = session_manager.get_session(sender_id)
                
                try:
                    # Handle text messages
                    if 'message' in messaging_event:
                        if 'text' in messaging_event['message']:
                            message_text = messaging_event['message']['text']
                            analytics.log_interaction(sender_id, 'text_message', message_text)
                            import asyncio
                            asyncio.run(handle_text_message(sender_id, message_text))
                        
                        # Handle quick replies
                        if 'quick_reply' in messaging_event['message']:
                            payload = messaging_event['message']['quick_reply']['payload']
                            analytics.log_interaction(sender_id, 'quick_reply', payload)
                            response = menu_manager.handle_payload(payload, session)
                            send_message(sender_id, response)
                    
                    # Handle postback buttons
                    if 'postback' in messaging_event:
                        payload = messaging_event['postback']['payload']
                        analytics.log_interaction(sender_id, 'postback', payload)
                        response = menu_manager.handle_payload(payload, session)
                        send_message(sender_id, response)
                
                except Exception as e:
                    logger.error(f"Error handling message: {str(e)}")
                    error_message = {"text": "عذراً، حدث خطأ. الرجاء المحاولة مرة أخرى."}
                    send_message(sender_id, error_message)
                
                # Update analytics
                analytics.update_daily_metric('total_messages')
                    
    return 'OK', 200

def handle_postback(sender_id, payload):
    """Handle postback from buttons"""
    # Example postback handling
    response = {"text": f"Selected option: {payload}"}
    send_message(sender_id, response)

# Example functions for different message types
def send_button_template(recipient_id, text, buttons):
    """Send button template"""
    template_data = {
        "template_type": "button",
        "text": text,
        "buttons": buttons
    }
    send_template_message(recipient_id, template_data)

def send_generic_template(recipient_id, elements):
    """Send generic template (cards)"""
    template_data = {
        "template_type": "generic",
        "elements": elements
    }
    send_template_message(recipient_id, template_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
