import sqlite3
import json
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.db_path = 'facebook_bot.db'
        self._init_db()
        
    def _init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create templates table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS templates (
                    name TEXT PRIMARY KEY,
                    data TEXT
                )
            ''')
            
            # Create conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    user_id TEXT PRIMARY KEY,
                    state TEXT
                )
            ''')
            
            # Create responses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS responses (
                    trigger TEXT PRIMARY KEY,
                    response TEXT,
                    confidence REAL,
                    learned BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create conversation history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    message TEXT,
                    response TEXT,
                    is_bot BOOLEAN,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    feedback INTEGER DEFAULT 0
                )
            ''')
            
            conn.commit()

    def save_template(self, template_name, template_data):
        """Save a new template to database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR REPLACE INTO templates (name, data) VALUES (?, ?)',
                (template_name, json.dumps(template_data))
            )
            conn.commit()
    
    def get_template(self, template_name):
        """Get template by name"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT data FROM templates WHERE name = ?', (template_name,))
            result = cursor.fetchone()
            return json.loads(result[0]) if result else None
    
    def list_templates(self):
        """Get all templates"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT name, data FROM templates')
            templates = []
            for row in cursor.fetchall():
                templates.append({
                    'name': row[0],
                    'data': json.loads(row[1])
                })
            return templates
    def save_conversation_state(self, user_id, state):
        """Save conversation state for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT OR REPLACE INTO conversations (user_id, state) VALUES (?, ?)',
                (user_id, json.dumps(state))
            )
            conn.commit()
    
    def get_conversation_state(self, user_id):
        """Get conversation state for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT state FROM conversations WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return json.loads(result[0]) if result else None
    
    def save_custom_response(self, trigger, response_data, confidence=None, learned=False):
        """Save custom response for specific trigger words"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT OR REPLACE INTO responses 
                (trigger, response, confidence, learned) 
                VALUES (?, ?, ?, ?)
                ''',
                (trigger, json.dumps(response_data), confidence, learned)
            )
            conn.commit()
    
    def get_custom_response(self, trigger):
        """Get custom response for trigger words"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT response, confidence, learned FROM responses WHERE trigger = ?',
                (trigger,)
            )
            result = cursor.fetchone()
            if result:
                return {
                    'text': json.loads(result[0]),
                    'confidence': result[1],
                    'learned': bool(result[2])
                }
            return None
            
    def save_conversation(self, user_id, message, response, is_bot=False):
        """Save conversation history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                INSERT INTO conversation_history 
                (user_id, message, response, is_bot) 
                VALUES (?, ?, ?, ?)
                ''',
                (user_id, message, response, is_bot)
            )
            conn.commit()
            return cursor.lastrowid
    
    def get_conversation(self, conversation_id):
        """Get specific conversation by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT user_id, message, response, is_bot FROM conversation_history WHERE id = ?',
                (conversation_id,)
            )
            result = cursor.fetchone()
            if result:
                return {
                    'user_id': result[0],
                    'message': result[1],
                    'response': result[2],
                    'is_bot': bool(result[3])
                }
            return None
    
    def get_conversation_history(self, user_id, limit=10):
        """Get conversation history for a user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT message, response, is_bot, timestamp
                FROM conversation_history
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
                ''',
                (user_id, limit)
            )
            return [
                {
                    'message': row[0],
                    'response': row[1],
                    'is_bot': bool(row[2]),
                    'timestamp': row[3]
                }
                for row in cursor.fetchall()
            ][::-1]  # Reverse to get chronological order
    
    def save_feedback(self, conversation_id, feedback):
        """Save user feedback for a conversation"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE conversation_history SET feedback = ? WHERE id = ?',
                (feedback, conversation_id)
            )
            conn.commit()
    
    def get_successful_responses(self, min_feedback=1):
        """Get responses that received positive feedback"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT message, response
                FROM conversation_history
                WHERE is_bot = 1 AND feedback >= ?
                ''',
                (min_feedback,)
            )
            return cursor.fetchall()
