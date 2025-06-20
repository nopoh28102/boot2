import openai
import os
from dotenv import load_dotenv
from logger import logger
from database import Database

load_dotenv()

class AIEngine:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('MODEL_NAME', 'gpt-3.5-turbo')
        self.max_history = int(os.getenv('MAX_HISTORY_MESSAGES', 10))
        self.db = Database()
        openai.api_key = self.api_key

    def get_conversation_prompt(self):
        """Get the base prompt for the conversation"""
        return """أنت مساعد خدمة عملاء ودود ومحترف. عليك:
1. الإجابة بأسلوب مهذب ومحترف
2. الحفاظ على المحادثة باللغة العربية
3. تقديم معلومات دقيقة ومفيدة
4. طلب توضيح إذا كان السؤال غير واضح
5. الاعتذار بلطف إذا لم تتمكن من المساعدة"""

    def prepare_messages(self, user_id, current_message):
        """Prepare conversation history for AI"""
        messages = [{"role": "system", "content": self.get_conversation_prompt()}]
        
        # Get conversation history
        history = self.db.get_conversation_history(user_id, limit=self.max_history)
        for msg in history:
            role = "assistant" if msg['is_bot'] else "user"
            messages.append({"role": role, "content": msg['message']})
        
        # Add current message
        messages.append({"role": "user", "content": current_message})
        return messages

    async def generate_response(self, user_id, message, context=None):
        """Generate AI response"""
        try:
            # Check for saved responses first
            saved_response = self.db.get_custom_response(message.lower())
            if saved_response:
                logger.info(f"Found saved response for: {message}")
                return saved_response

            # Prepare messages with context
            messages = self.prepare_messages(user_id, message)
            if context:
                # Add context as system message
                messages.insert(1, {
                    "role": "system",
                    "content": f"معلومات السياق: {context}"
                })

            # Get AI response
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500,
                presence_penalty=0.6
            )

            ai_response = response.choices[0].message['content']
            
            # Save the conversation
            self.db.save_conversation(
                user_id=user_id,
                message=message,
                response=ai_response,
                is_saved_response=False
            )

            return ai_response

        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return "عذراً، حدث خطأ. هل يمكنك إعادة صياغة سؤالك بطريقة أخرى؟"

    def learn_from_conversation(self, message, response, confidence_score=None):
        """Learn from successful conversations"""
        try:
            if confidence_score and confidence_score > 0.8:  # Only learn from high-confidence interactions
                # Clean and normalize the message
                cleaned_message = message.lower().strip()
                
                # Save as a custom response if it's not already saved
                if not self.db.get_custom_response(cleaned_message):
                    self.db.save_custom_response(cleaned_message, {
                        'text': response,
                        'confidence': confidence_score,
                        'learned': True
                    })
                    logger.info(f"Learned new response for: {cleaned_message}")

        except Exception as e:
            logger.error(f"Error learning from conversation: {str(e)}")

# Create global AI engine instance
ai_engine = AIEngine()
