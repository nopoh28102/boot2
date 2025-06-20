from database import Database
from datetime import datetime, timedelta
from collections import defaultdict

class StatsManager:
    def __init__(self):
        self.db = Database()
    
    def get_active_users(self, hours=24):
        """Get number of active users in last X hours"""
        since = datetime.now() - timedelta(hours=hours)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT COUNT(DISTINCT user_id)
                FROM conversation_history
                WHERE timestamp >= ?
                ''',
                (since,)
            )
            return cursor.fetchone()[0]
    
    def get_messages_today(self):
        """Get number of messages today"""
        today = datetime.now().date()
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT COUNT(*)
                FROM conversation_history
                WHERE DATE(timestamp) = ?
                ''',
                (today,)
            )
            return cursor.fetchone()[0]
    
    def get_satisfaction_rate(self):
        """Calculate satisfaction rate based on feedback"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT 
                    COUNT(CASE WHEN feedback > 0 THEN 1 END) * 100.0 / COUNT(*)
                FROM conversation_history
                WHERE feedback IS NOT NULL
                '''
            )
            rate = cursor.fetchone()[0]
            return round(rate if rate else 0, 1)
    
    def get_learned_responses_count(self):
        """Get count of learned responses"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT COUNT(*)
                FROM responses
                WHERE learned = 1
                '''
            )
            return cursor.fetchone()[0]
    
    def get_interaction_chart_data(self, days=7):
        """Get daily interaction data for chart"""
        since = datetime.now() - timedelta(days=days)
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as count
                FROM conversation_history
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date
                ''',
                (since,)
            )
            data = cursor.fetchall()
            
            # Fill in missing dates
            date_counts = defaultdict(int)
            for date, count in data:
                date_counts[date] = count
            
            dates = []
            counts = []
            current = since.date()
            end = datetime.now().date()
            
            while current <= end:
                dates.append(current.strftime('%Y-%m-%d'))
                counts.append(date_counts[current.strftime('%Y-%m-%d')])
                current += timedelta(days=1)
            
            return {
                'labels': dates,
                'interactions': counts
            }
    
    def get_response_types_distribution(self):
        """Get distribution of different response types"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # Count AI responses
            cursor.execute(
                '''
                SELECT COUNT(*)
                FROM conversation_history
                WHERE is_bot = 1 AND response LIKE '%AI generated%'
                '''
            )
            ai_count = cursor.fetchone()[0]
            
            # Count learned responses
            cursor.execute(
                '''
                SELECT COUNT(*)
                FROM conversation_history
                WHERE is_bot = 1 AND response LIKE '%learned%'
                '''
            )
            learned_count = cursor.fetchone()[0]
            
            # Count template responses
            cursor.execute(
                '''
                SELECT COUNT(*)
                FROM conversation_history
                WHERE is_bot = 1 AND response LIKE '%template%'
                '''
            )
            template_count = cursor.fetchone()[0]
            
            # Count custom responses
            cursor.execute(
                '''
                SELECT COUNT(*)
                FROM conversation_history
                WHERE is_bot = 1 
                AND response NOT LIKE '%AI generated%'
                AND response NOT LIKE '%learned%'
                AND response NOT LIKE '%template%'
                '''
            )
            custom_count = cursor.fetchone()[0]
            
            return [ai_count, learned_count, template_count, custom_count]
    
    def get_popular_topics(self, limit=10):
        """Get most popular conversation topics"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT 
                    CASE 
                        WHEN message LIKE '%استفسار%' THEN 'استفسار'
                        WHEN message LIKE '%مشكلة%' THEN 'مشكلة'
                        WHEN message LIKE '%طلب%' THEN 'طلب'
                        ELSE 'أخرى'
                    END as topic,
                    COUNT(*) as count
                FROM conversation_history
                WHERE is_bot = 0
                GROUP BY topic
                ORDER BY count DESC
                LIMIT ?
                ''',
                (limit,)
            )
            return [
                {'name': row[0], 'count': row[1]}
                for row in cursor.fetchall()
            ]
    
    def get_recent_feedback(self, limit=10):
        """Get recent user feedback"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''
                SELECT 
                    message,
                    feedback,
                    timestamp
                FROM conversation_history
                WHERE feedback IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT ?
                ''',
                (limit,)
            )
            return [
                {
                    'message': row[0],
                    'score': row[1],
                    'timestamp': row[2]
                }
                for row in cursor.fetchall()
            ]

# Create global stats manager instance
stats_manager = StatsManager()
