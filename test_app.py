#!/usr/bin/env python3
import os
import sys

# Set environment variables
os.environ['SESSION_SECRET'] = 'dev-secret-key-12345'
os.environ['ADMIN_PASSWORD'] = 'admin123'

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    print("✓ App import successful")
    
    # Test basic functionality
    with app.test_client() as client:
        response = client.get('/')
        print(f"✓ Home route status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Application is working correctly")
        else:
            print(f"✗ Application returned status code: {response.status_code}")
            
except Exception as e:
    print(f"✗ Error testing app: {str(e)}")
    import traceback
    traceback.print_exc()