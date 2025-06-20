import os
import sys

# Set environment variables first
os.environ['SESSION_SECRET'] = 'dev-secret-key-12345'
os.environ['ADMIN_PASSWORD'] = 'admin123'

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == '__main__':
    print("Starting Facebook Messenger Bot...")
    print("Server available at: http://localhost:5000")
    print("Admin panel: http://localhost:5000/admin/login")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)