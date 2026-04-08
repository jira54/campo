from django import template
from django.utils import timezone
import random

register = template.Library()

@register.simple_tag
def get_pulse_quote(persona):
    hour = timezone.localtime().hour
    
    # --- PERSONA: MSME (Growth Hustler) ---
    quotes_msme = {
        'morning': [
            "Hustle starts with a clean ledger and a sharp mind.",
            "Today's goal: Beat yesterday's record.",
            "Small sales build big empires. Let's get started."
        ],
        'day': [
            "Every customer is a partner in your growth.",
            "Keep the momentum. Excellence is a daily habit.",
            "Volume follows consistency. Focus on the next sale."
        ],
        'evening': [
            "Reflect on tonight's totals; tomorrow's strategy starts now.",
            "You built something today. Rest well, Hustler.",
            "Growth is incremental. You're 1% better than this morning."
        ]
    }
    
    # --- PERSONA: NGO (Impact Maker) ---
    quotes_ngo = {
        'morning': [
            "Integrity in data is transparency in your mission.",
            "Today, we transform numbers into human impact.",
            "Leadership is service. Lead your community today."
        ],
        'day': [
            "Accurate logging is the bedrock of donor trust.",
            "Every entry represents a life changed. Log with care.",
            "Audit-readiness is a daily practice, not a yearly event."
        ],
        'evening': [
            "The community sleeps better because of your work today.",
            "Data archived. Impact secured. Well done.",
            "Reflect on the lives touched today. Your mission continues."
        ]
    }
    
    # --- PERSONA: RESORT (Luxury Concierge) ---
    quotes_resort = {
        'morning': [
            "Excellence isn't a check-list; it's a feeling. Set the tone.",
            "3 VIP arrivals today. Let's make their first impression perfect.",
            "The resort is a stage. Your staff are the performers. Action."
        ],
        'day': [
            "Seamless service is invisible. Aim for harmony.",
            "Precision in folios prevents friction at check-out.",
            "A happy guest at the bar is a returning guest for the resort."
        ],
        'evening': [
            "The stars are out, and your guests are home. Great work today.",
            "Reflect on the guest comments. Every critique is a chance to refine.",
            "Luxury is consistency. Rest and prepare for another perfect day."
        ]
    }
    
    # Mapping
    persona_map = {
        'msme': quotes_msme,
        'ngo': quotes_ngo,
        'resort': quotes_resort
    }
    
    active_set = persona_map.get(persona, quotes_msme) # Default to MSME
    
    if 5 <= hour < 12:
        time_period = 'morning'
    elif 12 <= hour < 18:
        time_period = 'day'
    else:
        time_period = 'evening'
        
    return random.choice(active_set[time_period])
