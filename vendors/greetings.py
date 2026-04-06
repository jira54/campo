from datetime import datetime
import random

DAYS = {
    0: ("Monday", "", "New week, new opportunities!"),
    1: ("Tuesday", "", "Keep momentum going!"),
    2: ("Wednesday", "", "Halfway there — you're doing great!"),
    3: ("Thursday", "", "Almost weekend — Kidogo tuu!"),
    4: ("Friday", "", "End week strong!"),
    5: ("Saturday", "", "Weekend hustle hits different!"),
    6: ("Sunday", "", "Rest, reflect,we thank God and prepare for week!"),
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

RANDOM_MESSAGES = [
    "Here's a cozy sip ☕ Did you know octopuses have three hearts?",
    "Fresh vibes today 🌿 Honey never spoils, even after thousands of years.",
    "Quick fun fact! Bananas are technically berries.",
    "Nature wonder 🦋 A group of butterflies is called a flutter.",
    "Space fact! One day on Venus equals 243 Earth days.",
    "Animal magic 🐘 Elephants are the only animals that can't jump.",
    "Ocean mystery 🌊 95% of the ocean is still unexplored.",
    "Brain power! Your brain uses 20% of your body's energy.",
    "Tree wisdom 🌳 Some trees can live for over 4,000 years.",
    "Bird fact 🦅 Eagles can see up to 8 times better than humans.",
    "Sweet surprise 🍯 Bees communicate by dancing.",
    "Cloud magic ☁️ The average cloud weighs around 1 million pounds.",
    "Desert wonder 🌵 Cacti can live for over 200 years.",
    "Ocean giant 🐋 Blue whales are the largest animals ever known.",
    "Night sky 🌟 There are more stars than grains of sand on Earth.",
    "Plant power 🌱 Bamboo can grow up to 35 inches in one day.",
    "Insect world 🐛 Caterpillars have 12 eyes.",
    "Mountain majesty 🏔️ Mount Everest grows about 4mm per year.",
    "Water cycle 💧 A single tree can absorb 48 pounds of CO2 per year.",
    "Desert bloom 🌸 Some desert flowers bloom for just one day.",
]

RANDOM_TIPS = [
    "💪 Small steps today lead to big wins tomorrow. 📈",
    "🌟 Your consistency is building your success story. 📖",
    "🚀 Every customer interaction matters - make it count! 💎",
    "💡 One great idea can change everything today. ⚡",
    "🎯 Focus on progress, not perfection. 🎪",
    "🌱 Your business grows with every decision you make. 🌳",
    "⚡ Energy follows focus - choose your priority today. 🔑",
    "🏆 Winners are made from daily small victories. 🥇",
    "💎 Quality service creates loyal customers. 👥",
    "🔥 Your passion fuels your business growth. 🌟",
    "📈 Track your progress to celebrate your wins. 🎊",
    "🌸 Every challenge is an opportunity in disguise. 🎭",
    "💰 Smart decisions today build wealth tomorrow. 🏦",
    "🎨 Your unique approach is your competitive advantage. 🎪",
    "🌊 Go with the flow but stay focused on goals. 🧭",
    "🦅 Rise above challenges with confidence. 👑",
    "👑Your positive energy attracts success. 💫",
    "⭐ You're capable of amazing things today. ✨",
    "🎪 Bring joy to your work - customers feel it. 😊",
    "🌿 Growth happens outside your comfort zone. 🚪",
    "🔑 The key to success is starting today. 🏃‍♂️",
    "💫 Your dreams are valid and achievable. 🌌",
    "🌞 Bright moments are created by your actions. 🌅",
    "🎪 Make today memorable for your customers. 📸",
    "🏃‍♂️ Keep moving forward, even in small steps. 👣",
    "💚 Your business is making a difference. 🌍",
    "🎯 Today's efforts are tomorrow's results. 📅",
    "🌟 You're building something amazing! 🏗️",
    "🚀 Your potential is limitless today. 🌠",
    "💪 Strong businesses are built daily. 🧱",
    "🌸 Every customer interaction plants a seed. 🌱",
    "⚡ Your energy attracts the right customers. 🧲",
    "🎨 Your creativity is your superpower. 🦸‍♀️",
    "🌊 Adaptability is your greatest strength. 💪",
    "🦅 Soar above challenges with grace. 🕊️",
    "💫 Magic happens when you show up consistently. ✨",
    "🎯 Your focus creates your reality. 🌐",
    "🎯 Your positive impact ripples outward. 💧",
    "🔑 Today is your opportunity to shine. 🌟",
    "🌞 Your hard work is paying off. 💰",
    "🎪 Create moments customers remember. 🎭",
    "🏃‍♂️ Progress is progress, no matter how small. 📏",
    "💚 Your business serves your community. 🏘️",
    "🎯 Today's actions build tomorrow's success. 🏛️",
    "🌟 You're exactly where you need to be. 📍",
    "🚀 Your journey inspires others. 👀",
    "💪 Every day is a chance to grow. 📈",
    "🌸 Your kindness creates customer loyalty. ❤️",
    "⚡ Your enthusiasm is contagious. 😄",
    "🎨 Your unique style sets you apart. 🎪",
    "🌊 Flow with challenges, grow stronger. 🌊",
    "🦅 Your vision guides your success. 👁️",
    "💫 Believe in your business dreams. 💭",
    "🎯 Today's focus creates tomorrow's freedom. 🕊️",
    "💚Your authenticity attracts ideal customers. 🎯",
    "🔑 You hold the keys to your success. 🔐",
    "🌞 Your dedication is remarkable. 🏆",
    "🎪 Make business feel like play. 🎲",
    "🏃‍♂️ Small wins lead to big victories. 🏅",
    "💚 Your passion fuels your purpose. 🔥",
    "🎯 Today's effort compounds tomorrow. 📊",
    "💎 Your value is undeniable. 💍",
    "🌟 Shine bright in your business today! ☀️",
    "🚀 Launch your ideas with confidence. 🚁",
    "🌱 Nurture your business like a garden. 🌺",
    "🎨 Paint your success story today. 🖌️",
    "🌊 Navigate challenges like a captain. ⛵",
    "🦅 Fly high with your ambitions. ☁️",
    "💫 Create your own luck today. 🍀",
    "🎯 Hit your targets with precision. 🎯",
    "🌈 Color your business with joy. 🎨",
    "⚡ Charge forward with energy. ⚡",
    "🌟 Be the star of your industry. 🌟",
    "🏆 Celebrate every small win. 🎉",
    "🌸 Bloom where you're planted. 🌻",
    "🚀 Your business is taking off! ✈️",
    "💎 Polish your skills daily. 💎",
    "🌊 Make waves in your market. 🌊",
    "🦅 Lead with vision and courage. 👑",
    "💫 Your future is bright! 🌟",
    "🎯 Aim for excellence always. 🎯",
    "🌟 Bring color to your work. 🎨",
    "⚡ Spark innovation today! 💡",
    "🌟 You're a business superstar! ⭐",
    "🏆 Victory tastes sweet! 🍯",
    "🌱 Grow stronger daily. 🌳",
    "🚀 Skyrocket your success! 🚀",
    "💎 You're priceless! 💎",
    "🌟 Shine on! ✨",
]

from django.utils import timezone

def get_daily_context(user):
    today = timezone.now()
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
    
    # Get truly random messages
    random_message = random.choice(RANDOM_MESSAGES)
    random_tip = random.choice(RANDOM_TIPS)

    return {
        'greeting': greeting,
        'greeting_emoji': emoji,
        'day_name': day_name,
        'day_emoji': day_emoji,
        'day_message': day_message,
        'quote': QUOTES[weekday],
        'daily_tip': random_tip,
        'coffee_fact': random_message,
        'first_name': user.business_name.split()[0] if user.business_name else 'there',
    }
