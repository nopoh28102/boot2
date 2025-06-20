#!/usr/bin/env python3
import os
import sys

# Set environment variables before importing anything
os.environ['SESSION_SECRET'] = 'dev-secret-key-12345'
os.environ['ADMIN_PASSWORD'] = 'admin123'

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    
    if __name__ == '__main__':
        print("🚀 Starting Facebook Messenger Bot")
        print("📱 Homepage: http://localhost:5000")
        print("⚙️ Admin Panel: http://localhost:5000/admin/login")
        print("🔑 Admin Password: admin123")
        print("=" * 50)
        
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
        
except Exception as e:
    print(f"Error starting server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)