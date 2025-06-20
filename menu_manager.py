from database import Database
from logger import logger

class MenuItem:
    def __init__(self, title, payload=None, next_menu=None, action=None):
        self.title = title
        self.payload = payload
        self.next_menu = next_menu
        self.action = action

class Menu:
    def __init__(self, title, items=None):
        self.title = title
        self.items = items or []
    
    def add_item(self, item):
        """Add an item to the menu"""
        self.items.append(item)
    
    def to_quick_replies(self):
        """Convert menu to quick replies format"""
        return {
            "text": self.title,
            "quick_replies": [
                {
                    "content_type": "text",
                    "title": item.title,
                    "payload": item.payload
                }
                for item in self.items
            ]
        }
    
    def to_button_template(self):
        """Convert menu to button template format"""
        return {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": self.title,
                    "buttons": [
                        {
                            "type": "postback",
                            "title": item.title,
                            "payload": item.payload
                        }
                        for item in self.items[:3]  # Facebook limits to 3 buttons
                    ]
                }
            }
        }

class MenuManager:
    def __init__(self):
        self.menus = {}
        self.db = Database()
        self._initialize_default_menus()
    
    def _initialize_default_menus(self):
        """Initialize default menu structure"""
        # Main Menu
        main_menu = Menu("كيف يمكنني مساعدتك اليوم؟")
        main_menu.add_item(MenuItem("استفسار عن المنتجات", "PRODUCTS_INQUIRY"))
        main_menu.add_item(MenuItem("خدمة العملاء", "CUSTOMER_SERVICE"))
        main_menu.add_item(MenuItem("تقديم شكوى", "SUBMIT_COMPLAINT"))
        self.menus['MAIN'] = main_menu
        
        # Products Menu
        products_menu = Menu("ما نوع المنتج الذي تريد الاستفسار عنه؟")
        products_menu.add_item(MenuItem("المنتج الأول", "PRODUCT_1"))
        products_menu.add_item(MenuItem("المنتج الثاني", "PRODUCT_2"))
        products_menu.add_item(MenuItem("القائمة الرئيسية", "MAIN_MENU"))
        self.menus['PRODUCTS'] = products_menu
        
        # Customer Service Menu
        cs_menu = Menu("كيف يمكننا مساعدتك؟")
        cs_menu.add_item(MenuItem("التحدث مع موظف", "TALK_TO_AGENT"))
        cs_menu.add_item(MenuItem("الأسئلة الشائعة", "FAQ"))
        cs_menu.add_item(MenuItem("القائمة الرئيسية", "MAIN_MENU"))
        self.menus['CUSTOMER_SERVICE'] = cs_menu
    
    def get_menu(self, menu_id):
        """Get a menu by its ID"""
        return self.menus.get(menu_id)
    
    def handle_payload(self, payload, session):
        """Handle menu selection payload"""
        logger.info(f"Handling payload: {payload} for user: {session.user_id}")
        
        if payload == "MAIN_MENU":
            return self.menus['MAIN'].to_quick_replies()
        
        # Handle menu navigation
        for menu_id, menu in self.menus.items():
            for item in menu.items:
                if item.payload == payload:
                    if item.next_menu:
                        next_menu = self.get_menu(item.next_menu)
                        if next_menu:
                            session.update_session(new_state=item.next_menu)
                            return next_menu.to_quick_replies()
                    if item.action:
                        return item.action(session)
        
        # Default to main menu if payload not found
        logger.warning(f"Unknown payload: {payload}")
        return self.menus['MAIN'].to_quick_replies()

# Create global menu manager instance
menu_manager = MenuManager()
