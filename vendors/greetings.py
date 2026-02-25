from datetime import datetime

DAYS = {
    0: ("Monday", "🌟", "New week, new opportunities!"),
    1: ("Tuesday", "🔥", "Keep the momentum going!"),
    2: ("Wednesday", "💪", "Halfway there — you're doing great!"),
    3: ("Thursday", "🚀", "Almost the weekend — Kidogo tuu!"),
    4: ("Friday", "🎉", "End the week strong!"),
    5: ("Saturday", "💰", "Weekend hustle hits different!"),
    6: ("Sunday", "🌅", "Rest, reflect,we thank God and prepare for the week!"),
}

QUOTES = {
    0: "Every big business started with one customer. Keep building.",
    1: "Consistency is what transforms average into excellence.",
    2: "Your reputation is built one customer at a time.",
    3: "Small daily improvements lead to stunning results.",
    4: "The best marketing is a happy customer.",
    5: "Hustle now so your future self can thank you.",
    6: "Plan tomorrow today. Success loves preparation.",
}

TIPS = {
    0: "💡 Tip: Start the week by checking your at-risk customers and sending a promo.",
    1: "💡 Tip: Upsell one extra item to every customer today — it adds up fast.",
    2: "💡 Tip: Ask a regular customer for feedback today. It builds loyalty.",
    3: "💡 Tip: Log every sale today — accurate data = better decisions.",
    4: "💡 Tip: Thank your most loyal customer personally today.",
    5: "💡 Tip: Weekends are busiest — make sure your stock is ready.",
    6: "💡 Tip: Review last week's numbers and set a target for next week.",
}

def get_daily_context(user):
    today = datetime.now()
    weekday = today.weekday()
    hour = today.hour

    if hour < 12:
        greeting = "Good morning"
        emoji = "☀️"
    elif hour < 17:
        greeting = "Good afternoon"
        emoji = "🌤️"
    else:
        greeting = "Good evening"
        emoji = "🌙"

    day_name, day_emoji, day_message = DAYS[weekday]

    return {
        'greeting': greeting,
        'greeting_emoji': emoji,
        'day_name': day_name,
        'day_emoji': day_emoji,
        'day_message': day_message,
        'quote': QUOTES[weekday],
        'daily_tip': TIPS[weekday],
        'first_name': user.business_name.split()[0] if user.business_name else 'there',
    }
