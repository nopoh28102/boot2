from database import Database
from datetime import datetime, timedelta

class ConversationSession:
    def __init__(self, user_id):
        self.user_id = user_id
        self.current_state = None
        self.context = {}
        self.last_interaction = None
        self.db = Database()
    
    def start_session(self):
        """Initialize or resume a session"""
        stored_state = self.db.get_conversation_state(self.user_id)
        if stored_state:
            self.current_state = stored_state.get('state')
            self.context = stored_state.get('context', {})
            last_interaction = stored_state.get('last_interaction')
            if last_interaction:
                self.last_interaction = datetime.fromisoformat(last_interaction)
        else:
            self.current_state = 'START'
            self.context = {}
            self.last_interaction = datetime.now()
    
    def update_session(self, new_state=None, **context_updates):
        """Update session state and context"""
        if new_state:
            self.current_state = new_state
        
        self.context.update(context_updates)
        self.last_interaction = datetime.now()
        
        # Save to database
        session_data = {
            'state': self.current_state,
            'context': self.context,
            'last_interaction': self.last_interaction.isoformat()
        }
        self.db.save_conversation_state(self.user_id, session_data)
    
    def is_session_expired(self, timeout_minutes=30):
        """Check if session has expired"""
        if not self.last_interaction:
            return True
        
        expiration_time = datetime.now() - timedelta(minutes=timeout_minutes)
        return self.last_interaction < expiration_time
    
    def end_session(self):
        """End the current session"""
        self.current_state = 'END'
        self.context = {}
        self.update_session()

class SessionManager:
    def __init__(self):
        self.active_sessions = {}
    
    def get_session(self, user_id):
        """Get or create a session for a user"""
        if user_id not in self.active_sessions:
            session = ConversationSession(user_id)
            session.start_session()
            self.active_sessions[user_id] = session
        
        session = self.active_sessions[user_id]
        if session.is_session_expired():
            session.start_session()
        
        return session
    
    def end_session(self, user_id):
        """End a user's session"""
        if user_id in self.active_sessions:
            self.active_sessions[user_id].end_session()
            del self.active_sessions[user_id]
