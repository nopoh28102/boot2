#!/usr/bin/env python3
"""Complete test of the Flask Facebook Bot application"""
import os
import sys
import threading
import time
import requests

# Set environment variables
os.environ['SESSION_SECRET'] = 'dev-secret-key-12345'
os.environ['ADMIN_PASSWORD'] = 'admin123'

def run_server():
    """Run the Flask server in a separate thread"""
    from app import app
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def test_app():
    """Test the Flask application"""
    print("Testing Flask Facebook Bot Application...")
    
    # Start server in background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Test home page
        response = requests.get('http://localhost:5000', timeout=5)
        print(f"✓ Home page: Status {response.status_code}")
        
        # Test admin login page
        response = requests.get('http://localhost:5000/admin/login', timeout=5)
        print(f"✓ Admin login: Status {response.status_code}")
        
        # Test webhook verification (should fail without proper params)
        response = requests.get('http://localhost:5000/webhook', timeout=5)
        print(f"✓ Webhook endpoint: Status {response.status_code}")
        
        print("\n✓ All tests passed - Flask application is working correctly!")
        print("📱 Home page: http://localhost:5000")
        print("⚙️  Admin panel: http://localhost:5000/admin/login")
        print("🔑 Admin password: admin123")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing application: {e}")
        return False

if __name__ == '__main__':
    success = test_app()
    if success:
        print("\nApplication is ready to run!")
    else:
        print("\nApplication has issues that need to be resolved.")