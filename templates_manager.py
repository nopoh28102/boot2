class TemplateManager:
    @staticmethod
    def create_button_template(text, buttons):
        """Create a button template"""
        return {
            "template_type": "button",
            "text": text,
            "buttons": buttons
        }

    @staticmethod
    def create_generic_template(elements):
        """Create a generic template (carousel)"""
        return {
            "template_type": "generic",
            "elements": elements
        }

    @staticmethod
    def create_quick_replies(text, quick_replies):
        """Create quick replies"""
        return {
            "text": text,
            "quick_replies": quick_replies
        }

    @staticmethod
    def create_media_template(media_type, url, buttons=None):
        """Create media template"""
        template = {
            "template_type": "media",
            "elements": [
                {
                    "media_type": media_type,
                    "url": url
                }
            ]
        }
        if buttons:
            template["elements"][0]["buttons"] = buttons
        return template

# Example templates
TEMPLATE_EXAMPLES = {
    "welcome": {
        "text": "مرحباً بك! كيف يمكنني مساعدتك اليوم؟",
        "quick_replies": [
            {
                "content_type": "text",
                "title": "خدمة العملاء",
                "payload": "CUSTOMER_SERVICE"
            },
            {
                "content_type": "text",
                "title": "منتجاتنا",
                "payload": "PRODUCTS"
            }
        ]
    },
    "product_carousel": {
        "elements": [
            {
                "title": "المنتج الأول",
                "subtitle": "وصف المنتج",
                "image_url": "URL_TO_IMAGE",
                "buttons": [
                    {
                        "type": "postback",
                        "title": "تفاصيل",
                        "payload": "PRODUCT_1_DETAILS"
                    }
                ]
            }
        ]
    }
}
