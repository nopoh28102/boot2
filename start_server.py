#!/usr/bin/env python3
import os
import sys

# Set required environment variables
os.environ['SESSION_SECRET'] = 'dev-secret-key-12345'
os.environ['ADMIN_PASSWORD'] = 'admin123'

# Import and run the Flask application
from app import app

if __name__ == '__main__':
    print("Starting Flask Facebook Bot Application...")
    print("Home page: http://0.0.0.0:5000")
    print("Admin panel: http://0.0.0.0:5000/admin/login")
    print("Admin password: admin123")
    
    app.run(host='0.0.0.0', port=5000, debug=True)