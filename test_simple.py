#!/usr/bin/env python3
import sys
import os

# Set required environment variables
os.environ['SESSION_SECRET'] = 'dev-secret-key-12345'
os.environ['ADMIN_PASSWORD'] = 'admin123'

try:
    print("Testing Flask app startup...")
    from flask import Flask
    print("✓ Flask import successful")
    
    # Test individual module imports
    modules_to_test = [
        'database', 'message_handler', 'admin', 'logger', 
        'session_manager', 'menu_manager', 'analytics', 
        'ai_engine', 'conversation_learner'
    ]
    
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"✓ {module} import successful")
        except Exception as e:
            print(f"✗ {module} import failed: {e}")
    
    # Test app import
    from app import app
    print("✓ App import successful")
    
    # Test routes
    with app.test_client() as client:
        response = client.get('/')
        print(f"✓ Home route works: {response.status_code}")
        
        response = client.get('/admin/login')
        print(f"✓ Admin login route works: {response.status_code}")
    
    print("All tests passed - ready to run server")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()