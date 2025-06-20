from database import Database
from logger import Logger
from collections import defaultdict
import json
import re

class ConversationLearner:
    def __init__(self):
        self.db = Database()
        self.logger = Logger()
        self.response_patterns = defaultdict(list)
        self.load_learned_responses()
    
    def load_learned_responses(self):
        """Load previously learned responses"""
        try:
            responses = self.db.get_successful_responses()
            for message, response in responses:
                cleaned_message = self.clean_message(message)
                self.response_patterns[cleaned_message].append(response)
        except Exception as e:
            self.logger.error(f"Error loading learned responses: {str(e)}")
    
    def clean_message(self, message):
        """Clean and normalize message text"""
        # Convert to lowercase and remove extra whitespace
        message = message.lower().strip()
        # Remove punctuation
        message = re.sub(r'[^\w\s]', '', message)
        # Normalize Arabic text
        message = self.normalize_arabic(message)
        return message
    
    def normalize_arabic(self, text):
        """Normalize Arabic text by removing diacritics and normalizing characters"""
        # Remove Arabic diacritics
        text = re.sub(r'[\u064B-\u065F]', '', text)
        # Normalize Arabic characters
        replacements = {
            'أ': 'ا',
            'إ': 'ا',
            'آ': 'ا',
            'ة': 'ه',
            'ى': 'ي',
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        return text
    
    def find_similar_message(self, message, threshold=0.8):
        """Find similar message in learned responses"""
        cleaned_message = self.clean_message(message)
        best_match = None
        best_score = 0
        
        for learned_message in self.response_patterns.keys():
            score = self.calculate_similarity(cleaned_message, learned_message)
            if score > threshold and score > best_score:
                best_match = learned_message
                best_score = score
        
        return best_match, best_score
    
    def calculate_similarity(self, message1, message2):
        """Calculate similarity between two messages"""
        # Simple word overlap similarity for now
        # Could be improved with more sophisticated algorithms
        words1 = set(message1.split())
        words2 = set(message2.split())
        
        if not words1 or not words2:
            return 0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def learn_from_feedback(self, conversation_id, feedback):
        """Learn from user feedback"""
        if feedback > 0:  # Positive feedback
            try:
                # Get the conversation
                conversation = self.db.get_conversation(conversation_id)
                if conversation and conversation['is_bot']:
                    # Add to learned responses
                    cleaned_message = self.clean_message(conversation['message'])
                    self.response_patterns[cleaned_message].append(conversation['response'])
                    
                    # Save to database
                    self.db.save_custom_response(
                        cleaned_message,
                        json.dumps({
                            'text': conversation['response'],
                            'learned': True,
                            'feedback_score': feedback
                        })
                    )
            except Exception as e:
                self.logger.error(f"Error learning from feedback: {str(e)}")
    
    def get_learned_response(self, message):
        """Get learned response for a message"""
        similar_message, confidence = self.find_similar_message(message)
        
        if similar_message and self.response_patterns[similar_message]:
            # Return the most recent learned response
            response = self.response_patterns[similar_message][-1]
            return {
                'text': response,
                'confidence': confidence,
                'learned': True
            }
        
        return None

# Create global conversation learner instance
conversation_learner = ConversationLearner()
