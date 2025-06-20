from templates_manager import TemplateManager

class MessageHandler:
    def __init__(self, send_message_func):
        self.send_message = send_message_func
        self.template_manager = TemplateManager()

    def handle_text_message(self, sender_id, message_text):
        """Handle incoming text messages and determine appropriate response"""
        message_text = message_text.lower()
        
        # Example handling different message types
        if "مرحبا" in message_text or "السلام عليكم" in message_text:
            self.send_welcome_message(sender_id)
        elif "منتجات" in message_text:
            self.send_product_catalog(sender_id)
        else:
            # Default response
            response = {"text": "شكراً لتواصلك معنا. كيف يمكنني مساعدتك؟"}
            self.send_message(sender_id, response)

    def send_welcome_message(self, sender_id):
        """Send welcome message with quick replies"""
        welcome_template = TemplateManager.create_quick_replies(
            "مرحباً بك! كيف يمكنني مساعدتك اليوم؟",
            [
                {
                    "content_type": "text",
                    "title": "استفسار",
                    "payload": "INQUIRY"
                },
                {
                    "content_type": "text",
                    "title": "منتجاتنا",
                    "payload": "PRODUCTS"
                },
                {
                    "content_type": "text",
                    "title": "تواصل معنا",
                    "payload": "CONTACT"
                }
            ]
        )
        self.send_message(sender_id, welcome_template)

    def send_product_catalog(self, sender_id):
        """Send product catalog as a generic template"""
        products_template = TemplateManager.create_generic_template([
            {
                "title": "المنتج الأول",
                "subtitle": "وصف تفصيلي للمنتج",
                "image_url": "https://example.com/product1.jpg",
                "buttons": [
                    {
                        "type": "postback",
                        "title": "تفاصيل",
                        "payload": "PRODUCT_1_DETAILS"
                    },
                    {
                        "type": "web_url",
                        "title": "شراء",
                        "url": "https://example.com/buy/product1"
                    }
                ]
            }
        ])
        self.send_message(sender_id, {"attachment": {"type": "template", "payload": products_template}})

    def send_audio_message(self, sender_id, audio_url):
        """Send audio message"""
        self.send_message(sender_id, {
            "attachment": {
                "type": "audio",
                "payload": {"url": audio_url}
            }
        })

    def send_image_message(self, sender_id, image_url):
        """Send image message"""
        self.send_message(sender_id, {
            "attachment": {
                "type": "image",
                "payload": {"url": image_url}
            }
        })
