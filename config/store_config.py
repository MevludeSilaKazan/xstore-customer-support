"""
XStore Configuration
Edit these values to customize for your store.
"""

STORE = {
    # Store Info
    "name": "XStore",
    "category": "Fashion & Clothing",
    
    # Return Policy
    "return_days": 14,
    "return_free": True,
    
    # Shipping
    "free_shipping_limit": 1200,  # TL
    "shipping_cost": 49.90,       # TL
    "shipping_days": "2-4 iş günü",
    "shipping_days_en": "2-4 business days",
    
    # Contact
    "working_hours": "09:00 - 18:00 (Hafta içi)",
    "working_hours_en": "09:00 - 18:00 (Weekdays)",
    "phone": "0850 XXX XX XX",
    "email": "destek@xstore.com",
    "instagram": "@xstore",
    
    # Campaigns
    "welcome_code_tr": "HOSGELDIN",
    "welcome_code_en": "WELCOME10",
    "welcome_discount": 10,  # percent
}

# Size Guide
SIZE_GUIDE = {
    "XS": {"tr": "32-34 beden, göğüs 82-86cm", "en": "US 0-2, Chest 32-34\" (82-86cm)"},
    "S":  {"tr": "36-38 beden, göğüs 86-90cm", "en": "US 4-6, Chest 34-35\" (86-90cm)"},
    "M":  {"tr": "38-40 beden, göğüs 90-94cm", "en": "US 8-10, Chest 35-37\" (90-94cm)"},
    "L":  {"tr": "40-42 beden, göğüs 94-98cm", "en": "US 10-12, Chest 37-39\" (94-98cm)"},
    "XL": {"tr": "42-44 beden, göğüs 98-102cm", "en": "US 14-16, Chest 39-40\" (98-102cm)"},
}

# Installment Plans
INSTALLMENTS = {
    100: 3,   # 100 TL and above: 3 installments
    300: 6,   # 300 TL and above: 6 installments
    500: 9,   # 500 TL and above: 9 installments
}

# Categories
CATEGORIES = [
    "product",   # Product & Size
    "order",     # Order & Shipping
    "return",    # Return & Exchange
    "payment",   # Payment & Invoice
    "account",   # Account & Membership
    "campaign",  # Campaigns & Discounts
    "general",   # General Info
]
