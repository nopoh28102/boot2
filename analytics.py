import sqlite3
from datetime import datetime, timedelta
import json
from logger import logger

class Analytics:
    def __init__(self, db_path='facebook_bot.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize analytics tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create interactions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    interaction_type TEXT,
                    content TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create metrics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    date DATE,
                    metric_name TEXT,
                    value INTEGER,
                    PRIMARY KEY (date, metric_name)
                )
            ''')
            
            conn.commit()
    
    def log_interaction(self, user_id, interaction_type, content):
        """Log a user interaction"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO interactions (user_id, interaction_type, content) VALUES (?, ?, ?)',
                    (user_id, interaction_type, json.dumps(content))
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Error logging interaction: {str(e)}")
    
    def update_daily_metric(self, metric_name, increment=1):
        """Update daily metric counter"""
        today = datetime.now().date()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO metrics (date, metric_name, value)
                    VALUES (?, ?, ?)
                    ON CONFLICT(date, metric_name) DO UPDATE SET
                    value = value + ?
                ''', (today, metric_name, increment, increment))
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating metric: {str(e)}")
    
    def get_user_stats(self, days=7):
        """Get user interaction statistics"""
        start_date = datetime.now() - timedelta(days=days)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        COUNT(DISTINCT user_id) as unique_users,
                        COUNT(*) as total_interactions,
                        AVG(interactions_per_user) as avg_interactions_per_user
                    FROM (
                        SELECT 
                            user_id,
                            COUNT(*) as interactions_per_user
                        FROM interactions
                        WHERE timestamp >= ?
                        GROUP BY user_id
                    )
                ''', (start_date,))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return None
    
    def get_popular_interactions(self, limit=10):
        """Get most common interaction types"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        interaction_type,
                        COUNT(*) as count
                    FROM interactions
                    GROUP BY interaction_type
                    ORDER BY count DESC
                    LIMIT ?
                ''', (limit,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting popular interactions: {str(e)}")
            return []
    
    def generate_daily_report(self):
        """Generate daily analytics report"""
        try:
            today = datetime.now().date()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get today's metrics
                cursor.execute('''
                    SELECT metric_name, value
                    FROM metrics
                    WHERE date = ?
                ''', (today,))
                metrics = cursor.fetchall()
                
                # Get today's user activity
                cursor.execute('''
                    SELECT 
                        COUNT(DISTINCT user_id) as unique_users,
                        COUNT(*) as total_interactions
                    FROM interactions
                    WHERE date(timestamp) = ?
                ''', (today,))
                user_activity = cursor.fetchone()
                
                return {
                    'date': today.isoformat(),
                    'metrics': dict(metrics),
                    'unique_users': user_activity[0],
                    'total_interactions': user_activity[1]
                }
        except Exception as e:
            logger.error(f"Error generating daily report: {str(e)}")
            return None

# Create global analytics instance
analytics = Analytics()
