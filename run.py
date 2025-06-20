#!/usr/bin/env python3
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import app
    
    if __name__ == '__main__':
        # Set environment variables if not already set
        if not os.getenv('SESSION_SECRET'):
            os.environ['SESSION_SECRET'] = 'dev-secret-key-12345'
        if not os.getenv('ADMIN_PASSWORD'):
            os.environ['ADMIN_PASSWORD'] = 'admin123'
        
        print("🚀 تم تشغيل بوت فيسبوك الذكي")
        print("📱 الصفحة الرئيسية: http://localhost:5000")
        print("⚙️  لوحة التحكم: http://localhost:5000/admin/login")
        print("🔑 كلمة مرور الإدارة: admin123")
        print("=" * 50)
        
        # Run the Flask app
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
        
except ImportError as e:
    print(f"خطأ في الاستيراد: {e}")
    sys.exit(1)
except Exception as e:
    print(f"خطأ في التشغيل: {e}")
    sys.exit(1)