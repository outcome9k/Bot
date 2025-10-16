import os
import telebot
import re
import json
import requests
import time
import random
import threading
from telebot import types
from datetime import datetime, timedelta
from faker import Faker
from multiprocessing import Process

# Environment variable ကနေ token ယူပါ
token = os.getenv('BOT_TOKEN')
admin = 6998791194

if not token:
    print("❌ ERROR: BOT_TOKEN environment variable is missing!")
    print("💡 Please add BOT_TOKEN in Railway Variables")
    exit(1)

bot = telebot.TeleBot(token, parse_mode="HTML")
f = Faker()
stopuser = {}
command_usage = {}

def get_bin_info(bin_number):
    """Get BIN information from your API"""
    try:
        api_url = f"https://chkr-api.vercel.app/api/check?cc={bin_number}|06|2027|402"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if the request was successful
            if data.get('code') == 0:  # Successful response
                card_info = data.get('card', {})
                country_info = card_info.get('country', {})
                
                return {
                    'level': card_info.get('category', 'Unknown'),
                    'bank': card_info.get('bank', 'Unknown'),
                    'country': country_info.get('name', 'Unknown'),
                    'country_flag': country_info.get('emoji', '🇺🇸'),
                    'brand': card_info.get('brand', 'Unknown'),
                    'type': card_info.get('type', 'Unknown'),
                    'scheme': card_info.get('type', 'Unknown')
                }
            else:
                # If API returned error, use fallback
                print(f"BIN API Error: {data.get('message', 'Unknown error')}")
                
    except Exception as e:
        print(f"BIN API Error: {e}")
    
    # Final fallback
    return {
        'level': 'Unknown',
        'bank': 'Unknown', 
        'country': 'Unknown',
        'country_flag': '🇺🇸',
        'brand': 'Unknown',
        'type': 'Unknown',
        'scheme': 'Unknown'
    }

def reg(text):
    """Extract card details from text using regex"""
    try:
        # Pattern for card number|mm|yy|cvv
        pattern = r'(\d{16})\|(\d{2})\|(\d{2,4})\|(\d{3,4})'
        match = re.search(pattern, text)
        
        if match:
            card = match.group(1)
            mm = match.group(2)
            yy = match.group(3)
            cvv = match.group(4)
            
            # Format year to 4 digits if it's 2 digits
            if len(yy) == 2:
                yy = "20" + yy
            
            return f"{card}|{mm}|{yy}|{cvv}"
        else:
            return "None"
    except Exception as e:
        return "None"

def Tele(cc):
    """Braintree Auth Gateway - Using your API"""
    try:
        api_url = f"https://chkr-api.vercel.app/api/check?cc={cc}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'Unknown')
            message = data.get('message', 'No message')
            
            if status == 'Live':
                return "Approved"
            elif status == 'Die':
                return "Declined"
            else:
                return f"{status}: {message}"
        else:
            return "API Error"
    except Exception as e:
        return f"Error: {str(e)}"

def st(cc):
    """Stripe Charge Gateway - Using your API"""
    try:
        api_url = f"https://chkr-api.vercel.app/api/check?cc={cc}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'Unknown')
            message = data.get('message', 'No message')
            
            if status == 'Live':
                return "success"
            elif status == 'Die':
                return "declined"
            else:
                return f"{status}: {message}"
        else:
            return "API Error"
    except Exception as e:
        return f"Error: {str(e)}"

def scc(cc):
    """Stripe Auth Gateway - Using your API"""
    try:
        api_url = f"https://chkr-api.vercel.app/api/check?cc={cc}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'Unknown')
            message = data.get('message', 'No message')
            
            if status == 'Live':
                return "Funds available"
            elif status == 'Die':
                return "Authentication failed"
            else:
                return f"{status}: {message}"
        else:
            return "API Error"
    except Exception as e:
        return f"Error: {str(e)}"

def vbv(cc):
    """3D Lookup Gateway - Using your API"""
    try:
        api_url = f"https://chkr-api.vercel.app/api/check?cc={cc}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'Unknown')
            message = data.get('message', 'No message')
            
            if status == 'Live':
                return "Authenticate Attempt Successful"
            elif status == 'Die':
                return "Authenticate Frictionless Failed"
            else:
                return f"{status}: {message}"
        else:
            return "API Error"
    except Exception as e:
        return f"Error: {str(e)}"

def reset_command_usage():
    for user_id in command_usage:
        command_usage[user_id] = {'count': 0, 'last_time': None}

def check_subscription(user_id):
    """Check if user has valid subscription"""
    # Admin always has access
    if user_id == admin:
        return True, "ADMIN 🔥"
        
    try:
        # Railway မှာ file system access မရှိတဲ့အတွက် temporary solution
        # Production မှာ database သုံးသင့်ပါတယ်
        return True, "PREMIUM"  # Temporary - all users have access for testing
        
    except Exception as e:
        print(f"Subscription check error: {e}")
        return True, "PREMIUM"  # Temporary for testing

@bot.message_handler(commands=["start"])
def start(message):
    def my_function():
        name = message.from_user.first_name
        user_id = message.from_user.id
        
        # Check subscription
        has_sub, plan_status = check_subscription(user_id)
                
        if plan_status == 'FREE':    
            keyboard = types.InlineKeyboardMarkup()
            ahmed = types.InlineKeyboardButton(text="✨ OWNER ✨", url="https://t.me/Outcome9k")
            contact_button = types.InlineKeyboardButton(text="✨ CHANNEL ✨", url="https://t.me/Outcome9k")
            keyboard.add(contact_button, ahmed)
            video_url = 'https://t.me/rokanxs/2'
            bot.send_video(chat_id=message.chat.id, video=video_url, caption=f'''<b>HELLO {name}
THIS PARTICULAR BOT IS NOT FREE 
IF YOU WANT TO USE IT, YOU MUST PURCHASE A WEEKLY OR MONTHLY SUBSCRIPTION 

THE BOT'S JOB IS TO CHECK CARDS

BOT SUBSCRIPTION PRICES:
 
THAILAND 🇹🇭
1 WEEK » 100 BAHT
1 MONTH » 200 BAHT
━━━━━━━━━━━━

CLICK /CMDS TO VIEW THE COMMANDS

YOUR PLAN NOW {plan_status}</b>
    ''', reply_markup=keyboard)
            return
            
        keyboard = types.InlineKeyboardMarkup()
        contact_button = types.InlineKeyboardButton(text="✨ OWNER ✨", url="https://t.me/Outcome9k")
        ahmed = types.InlineKeyboardButton(text="✨ CHANNEL ✨", url="https://t.me/Outcome9k")
        keyboard.add(contact_button, ahmed)
        video_url = 'https://t.me/rokanxs/2'
        bot.send_video(chat_id=message.chat.id, video=video_url, caption=f'''<b>Welcome {name}!

Your Plan: {plan_status}

Click /cmds To View The Commands Or Send The File And I Will Check It</b>''', reply_markup=keyboard, parse_mode="HTML")
    my_thread = threading.Thread(target=my_function)
    my_thread.start()

@bot.message_handler(commands=["cmds"])
def show_commands(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    
    # Check subscription for plan display
    has_sub, plan_status = check_subscription(user_id)
    
    keyboard = types.InlineKeyboardMarkup()
    contact_button = types.InlineKeyboardButton(text=f"✨ {plan_status}  ✨", callback_data='plan')
    keyboard.add(contact_button)
    bot.send_message(chat_id=message.chat.id, text=f'''<b> 
🤖 BOT COMMANDS LIST
━━━━━━━━━━━━━━━━━━━━

🛒 CHECKING COMMANDS:
━━━━━━━━━━━━━━━━━━━━
• BRAINTREE AUTH » <code>/chk cc|mm|yy|cvv</code>
• STRIPE CHARGE » <code>/str cc|mm|yy|cvv</code>
• STRIPE AUTH » <code>/au cc|mm|yy|cvv</code>
• 3D LOOKUP » <code>/vbv cc|mm|yy|cvv</code>

📁 FILE CHECKING:
━━━━━━━━━━━━━━━━━━━━
• Send any text file containing cards
• Choose gateway from menu
• Supports multiple cards at once

🔧 OTHER COMMANDS:
━━━━━━━━━━━━━━━━━━━━
• /start - Start the bot
• /cmds - Show this commands list

📝 CARD FORMAT:
━━━━━━━━━━━━━━━━━━━━
<code>5301257400000000|03|2025|123</code>
<code>5301257400000000|03|25|123</code>

🎯 SUPPORTED GATEWAYS:
━━━━━━━━━━━━━━━━━━━━
✅ Braintree Auth
✅ Stripe Charge  
✅ Stripe Auth
✅ 3D Lookup

💎 YOUR PLAN: {plan_status}
🔧 Bot By: @Akira_fate</b>
''', reply_markup=keyboard, parse_mode="HTML")

@bot.message_handler(commands=["chk"])
def chk_command(message):
    """Braintree Auth command"""
    handle_single_check(message, "Braintree Auth", Tele)

@bot.message_handler(commands=["str"])
def str_command(message):
    """Stripe Charge command"""
    handle_single_check(message, "Stripe Charge", st)

@bot.message_handler(commands=["au"])
def au_command(message):
    """Stripe Auth command"""
    handle_single_check(message, "Stripe Auth", scc)

@bot.message_handler(commands=["vbv"])
def vbv_command(message):
    """3D Lookup command"""
    handle_single_check(message, "3D Lookup", vbv)

def handle_single_check(message, gate_name, gate_function):
    """Handle single card checking for all commands"""
    user_id = message.from_user.id
    name = message.from_user.first_name
    
    # Check subscription
    has_sub, plan_status = check_subscription(user_id)
    if not has_sub:
        if plan_status == "FREE":
            keyboard = types.InlineKeyboardMarkup()
            ahmed = types.InlineKeyboardButton(text="✨ OWNER ✨", url="https://t.me/Outcome9k")
            contact_button = types.InlineKeyboardButton(text="✨ CHANNEL ✨", url="https://t.me/Outcome9k")
            keyboard.add(contact_button, ahmed)
            bot.reply_to(message, f'''<b>HELLO {name}
THIS PARTICULAR BOT IS NOT FREE 
IF YOU WANT TO USE IT, YOU MUST PURCHASE A WEEKLY OR MONTHLY SUBSCRIPTION 

BOT SUBSCRIPTION PRICES:
 
THAILAND 🇹🇭
1 WEEK » 100 BAHT
1 MONTH » 200 BAHT
━━━━━━━━━━━━

YOUR PLAN NOW {plan_status}</b>''', reply_markup=keyboard)
        else:
            bot.reply_to(message, f'''<b>You Cannot Use The Bot Because Your Subscription Has Expired</b>''')
        return
    
    ko = bot.reply_to(message, "CHECKING YOUR CARD...⌛").message_id
    
    # Extract card
    try:
        cc = message.reply_to_message.text
    except:
        cc = message.text
    
    cc = str(reg(cc))
    if cc == 'None':
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text='''<b>Oops!
Please ensure you enter the card details in the correct format:
Card: XXXXXXXXXXXXXXXX|MM|YYYY|CVV</b>''', parse_mode="HTML")
        return
        
    start_time = time.time()
    try:
        last = str(gate_function(cc))
    except Exception as e:
        last = 'Error'
    
    # Get BIN information
    bin_data = get_bin_info(cc[:6])
    
    level = bin_data.get('level', 'Unknown')
    brand = bin_data.get('brand', 'Unknown')
    card_type = bin_data.get('type', 'Unknown')
    country = bin_data.get('country', 'Unknown')
    country_flag = bin_data.get('country_flag', '🇺🇸')
    bank = bin_data.get('bank', 'Unknown')
        
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Determine message based on response
    if any(x in last.lower() for x in ['approved', 'success', 'live', 'funds available', 'authenticate attempt successful']):
        status_emoji = "✅"
        status_text = "Approved"
    elif any(x in last.lower() for x in ['declined', 'die', 'authentication failed', 'authenticate frictionless failed']):
        status_emoji = "❌"
        status_text = "Declined"
    else:
        status_emoji = "⚠️"
        status_text = "Unknown"
    
    msg = f'''<b>{status_emoji} {status_text}

⸙ Card ➼ <code>{cc}</code>
⸙ Response ➼ {last}
⸙ Gateway ➼ {gate_name}		
⸙ Bin Info ➼ {cc[:6]} - {card_type} - {brand} - {level}
⸙ Country ➼ {country} - {country_flag} 
⸙ Issuer ➼ <code>{bank}</code>
⸙ Time ➼ {"{:.1f}".format(execution_time)}s
⸙ Plan ➼ {plan_status}
⸙ Bot By: @Akira_fate</b>'''
    
    bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text=msg, parse_mode="HTML")

@bot.message_handler(content_types=["document"])
def main(message):
    name = message.from_user.first_name
    user_id = message.from_user.id
    
    # Check subscription
    has_sub, plan_status = check_subscription(user_id)
    if not has_sub:
        if plan_status == "FREE":
            keyboard = types.InlineKeyboardMarkup()
            ahmed = types.InlineKeyboardButton(text="✨ OWNER ✨", url="https://t.me/Outcome9k")
            contact_button = types.InlineKeyboardButton(text="✨ CHANNEL ✨", url="https://t.me/Outcome9k")
            keyboard.add(contact_button, ahmed)
            bot.send_message(chat_id=message.chat.id, text=f'''<b>HELLO {name}
THIS PARTICULAR BOT IS NOT FREE 
IF YOU WANT TO USE IT, YOU MUST PURCHASE A WEEKLY OR MONTHLY SUBSCRIPTION 

YOUR PLAN NOW {plan_status}</b>''', reply_markup=keyboard)
        else:
            bot.reply_to(message, '''<b>You Cannot Use The Bot Because Your Subscription Has Expired</b>''')
        return
        
    # Railway မှာ file download မလုပ်နိုင်တဲ့အတွက် temporary message
    bot.reply_to(message, '''<b>📁 File checking is temporarily unavailable on this hosting.

Please use single card commands:
/chk cc|mm|yy|cvv
/str cc|mm|yy|cvv

Or contact owner for alternative.</b>''')

@bot.callback_query_handler(func=lambda call: call.data == 'str')
def stripe_callback(call):
    bot.answer_callback_query(call.id, "File checking temporarily unavailable. Use single card commands.")

@bot.callback_query_handler(func=lambda call: call.data == 'br')
def braintree_callback(call):
    bot.answer_callback_query(call.id, "File checking temporarily unavailable. Use single card commands.")

@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def stop_callback(call):
    bot.answer_callback_query(call.id, "Operation stopped")

print("🤖 Bot starting successfully...")
print(f"✅ Token loaded: {bool(token)}")

# Railway compatible polling
if __name__ == '__main__':
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"❌ Polling error: {e}")
        time.sleep(5)                    'bank': card_info.get('bank', 'Unknown'),
                    'country': country_info.get('name', 'Unknown'),
                    'country_flag': country_info.get('emoji', '🇺🇸'),
                    'brand': card_info.get('brand', 'Unknown'),
                    'type': card_info.get('type', 'Unknown'),
                    'scheme': card_info.get('type', 'Unknown')
                }
            else:
                # If API returned error, use fallback
                print(f"BIN API Error: {data.get('message', 'Unknown error')}")
                
    except Exception as e:
        print(f"BIN API Error: {e}")
    
    # Final fallback
    return {
        'level': 'Unknown',
        'bank': 'Unknown', 
        'country': 'Unknown',
        'country_flag': '🇺🇸',
        'brand': 'Unknown',
        'type': 'Unknown',
        'scheme': 'Unknown'
    }

def reg(text):
    """Extract card details from text using regex"""
    try:
        # Pattern for card number|mm|yy|cvv
        pattern = r'(\d{16})\|(\d{2})\|(\d{2,4})\|(\d{3,4})'
        match = re.search(pattern, text)
        
        if match:
            card = match.group(1)
            mm = match.group(2)
            yy = match.group(3)
            cvv = match.group(4)
            
            # Format year to 4 digits if it's 2 digits
            if len(yy) == 2:
                yy = "20" + yy
            
            return f"{card}|{mm}|{yy}|{cvv}"
        else:
            return "None"
    except Exception as e:
        return "None"

def Tele(cc):
    """Braintree Auth Gateway - Using your API"""
    try:
        api_url = f"https://chkr-api.vercel.app/api/check?cc={cc}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'Unknown')
            message = data.get('message', 'No message')
            
            if status == 'Live':
                return "Approved"
            elif status == 'Die':
                return "Declined"
            else:
                return f"{status}: {message}"
        else:
            return "API Error"
    except Exception as e:
        return f"Error: {str(e)}"

def st(cc):
    """Stripe Charge Gateway - Using your API"""
    try:
        api_url = f"https://chkr-api.vercel.app/api/check?cc={cc}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'Unknown')
            message = data.get('message', 'No message')
            
            if status == 'Live':
                return "success"
            elif status == 'Die':
                return "declined"
            else:
                return f"{status}: {message}"
        else:
            return "API Error"
    except Exception as e:
        return f"Error: {str(e)}"

def scc(cc):
    """Stripe Auth Gateway - Using your API"""
    try:
        api_url = f"https://chkr-api.vercel.app/api/check?cc={cc}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'Unknown')
            message = data.get('message', 'No message')
            
            if status == 'Live':
                return "Funds available"
            elif status == 'Die':
                return "Authentication failed"
            else:
                return f"{status}: {message}"
        else:
            return "API Error"
    except Exception as e:
        return f"Error: {str(e)}"

def vbv(cc):
    """3D Lookup Gateway - Using your API"""
    try:
        api_url = f"https://chkr-api.vercel.app/api/check?cc={cc}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'Unknown')
            message = data.get('message', 'No message')
            
            if status == 'Live':
                return "Authenticate Attempt Successful"
            elif status == 'Die':
                return "Authenticate Frictionless Failed"
            else:
                return f"{status}: {message}"
        else:
            return "API Error"
    except Exception as e:
        return f"Error: {str(e)}"

def reset_command_usage():
    for user_id in command_usage:
        command_usage[user_id] = {'count': 0, 'last_time': None}

def check_subscription(user_id):
    """Check if user has valid subscription"""
    # Admin always has access
    if user_id == admin:
        return True, "ADMIN"
        
    try:
        with open('data.json', 'r') as file:
            json_data = json.load(file)
        
        if str(user_id) not in json_data:
            return False, "FREE"
            
        user_data = json_data[str(user_id)]
        plan = user_data.get('plan', 'FREE')
        timer = user_data.get('timer', 'none')
        
        if plan == 'FREE':
            return False, "FREE"
            
        if timer == 'none':
            return False, "FREE"
            
        try:
            date_str = timer.split('.')[0]
            provided_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except:
            try:
                provided_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
            except:
                return False, "FREE"
                
        current_time = datetime.now()
        if current_time > provided_time:
            return False, "EXPIRED"
            
        return True, plan
        
    except Exception as e:
        print(f"Subscription check error: {e}")
        return False, "FREE"

@bot.message_handler(commands=["start"])
def start(message):
    def my_function():
        name = message.from_user.first_name
        user_id = message.from_user.id
        
        # Admin doesn't need to be in data.json
        if user_id != admin:
            with open('data.json', 'r') as file:
                json_data = json.load(file)
            
            try:
                BL = (json_data[str(user_id)]['plan'])
            except:
                BL = 'FREE'
                with open('data.json', 'r') as json_file:
                    existing_data = json.load(json_file)
                new_data = {
                    str(user_id): {
                        "plan": "FREE",
                        "timer": "none",
                    }
                }
        
                existing_data.update(new_data)
                with open('data.json', 'w') as json_file:
                    json.dump(existing_data, json_file, ensure_ascii=False, indent=4)
        else:
            BL = 'ADMIN 🔥'
                
        if BL == 'FREE':    
            keyboard = types.InlineKeyboardMarkup()
            ahmed = types.InlineKeyboardButton(text="✨ OWNER ✨", url="https://t.me/Outcome9k")
            contact_button = types.InlineKeyboardButton(text="✨ CHANNEL ✨", url="https://t.me/Outcome9k")
            keyboard.add(contact_button, ahmed)
            video_url = f'https://t.me/rokanxs/2'
            bot.send_video(chat_id=message.chat.id, video=video_url, caption=f'''<b>HELLO {name}
THIS PARTICULAR BOT IS NOT FREE 
IF YOU WANT TO USE IT, YOU MUST PURCHASE A WEEKLY OR MONTHLY SUBSCRIPTION 

THE BOT'S JOB IS TO CHECK CARDS

BOT SUBSCRIPTION PRICES:
 
THAILAND 🇹🇭
1 WEEK » 100 BAHT
1 MONTH » 200 BAHT
━━━━━━━━━━━━

CLICK /CMDS TO VIEW THE COMMANDS

YOUR PLAN NOW {BL}</b>
    ''', reply_markup=keyboard)
            return
            
        keyboard = types.InlineKeyboardMarkup()
        contact_button = types.InlineKeyboardButton(text="✨ OWNER ✨", url="https://t.me/Outcome9k")
        ahmed = types.InlineKeyboardButton(text="✨ CHANNEL ✨", url="https://t.me/Outcome9k")
        keyboard.add(contact_button, ahmed)
        video_url = f'https://t.me/rokanxs/2'
        bot.send_video(chat_id=message.chat.id, video=video_url, caption=f'''<b>Welcome {name}!

Your Plan: {BL}

Click /cmds To View The Commands Or Send The File And I Will Check It</b>''', reply_markup=keyboard, parse_mode="HTML")
    my_thread = threading.Thread(target=my_function)
    my_thread.start()

@bot.message_handler(commands=["cmds"])
def show_commands(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    
    # Check subscription for plan display
    has_sub, plan_status = check_subscription(user_id)
    
    keyboard = types.InlineKeyboardMarkup()
    contact_button = types.InlineKeyboardButton(text=f"✨ {plan_status}  ✨", callback_data='plan')
    keyboard.add(contact_button)
    bot.send_message(chat_id=message.chat.id, text=f'''<b> 
🤖 BOT COMMANDS LIST
━━━━━━━━━━━━━━━━━━━━

🛒 CHECKING COMMANDS:
━━━━━━━━━━━━━━━━━━━━
• BRAINTREE AUTH » <code>/chk cc|mm|yy|cvv</code>
• STRIPE CHARGE » <code>/str cc|mm|yy|cvv</code>
• STRIPE AUTH » <code>/au cc|mm|yy|cvv</code>
• 3D LOOKUP » <code>/vbv cc|mm|yy|cvv</code>

📁 FILE CHECKING:
━━━━━━━━━━━━━━━━━━━━
• Send any text file containing cards
• Choose gateway from menu
• Supports multiple cards at once

🔧 OTHER COMMANDS:
━━━━━━━━━━━━━━━━━━━━
• /start - Start the bot
• /cmds - Show this commands list

📝 CARD FORMAT:
━━━━━━━━━━━━━━━━━━━━
<code>5301257400000000|03|2025|123</code>
<code>5301257400000000|03|25|123</code>

🎯 SUPPORTED GATEWAYS:
━━━━━━━━━━━━━━━━━━━━
✅ Braintree Auth
✅ Stripe Charge  
✅ Stripe Auth
✅ 3D Lookup

💎 YOUR PLAN: {plan_status}
🔧 Bot By: @Akira_fate</b>
''', reply_markup=keyboard, parse_mode="HTML")

@bot.message_handler(commands=["chk"])
def chk_command(message):
    """Braintree Auth command"""
    handle_single_check(message, "Braintree Auth", Tele)

@bot.message_handler(commands=["str"])
def str_command(message):
    """Stripe Charge command"""
    handle_single_check(message, "Stripe Charge", st)

@bot.message_handler(commands=["au"])
def au_command(message):
    """Stripe Auth command"""
    handle_single_check(message, "Stripe Auth", scc)

@bot.message_handler(commands=["vbv"])
def vbv_command(message):
    """3D Lookup command"""
    handle_single_check(message, "3D Lookup", vbv)

def handle_single_check(message, gate_name, gate_function):
    """Handle single card checking for all commands"""
    user_id = message.from_user.id
    name = message.from_user.first_name
    
    # Check subscription
    has_sub, plan_status = check_subscription(user_id)
    if not has_sub:
        if plan_status == "FREE":
            keyboard = types.InlineKeyboardMarkup()
            ahmed = types.InlineKeyboardButton(text="✨ OWNER ✨", url="https://t.me/Outcome9k")
            contact_button = types.InlineKeyboardButton(text="✨ CHANNEL ✨", url="https://t.me/Outcome9k")
            keyboard.add(contact_button, ahmed)
            bot.reply_to(message, f'''<b>HELLO {name}
THIS PARTICULAR BOT IS NOT FREE 
IF YOU WANT TO USE IT, YOU MUST PURCHASE A WEEKLY OR MONTHLY SUBSCRIPTION 

BOT SUBSCRIPTION PRICES:
 
THAILAND 🇹🇭
1 WEEK » 100 BAHT
1 MONTH » 200 BAHT
━━━━━━━━━━━━

YOUR PLAN NOW {plan_status}</b>''', reply_markup=keyboard)
        else:
            bot.reply_to(message, f'''<b>You Cannot Use The Bot Because Your Subscription Has Expired</b>''')
        return
    
    ko = bot.reply_to(message, "CHECKING YOUR CARD...⌛").message_id
    
    # Extract card
    try:
        cc = message.reply_to_message.text
    except:
        cc = message.text
    
    cc = str(reg(cc))
    if cc == 'None':
        bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text='''<b>Oops!
Please ensure you enter the card details in the correct format:
Card: XXXXXXXXXXXXXXXX|MM|YYYY|CVV</b>''', parse_mode="HTML")
        return
        
    start_time = time.time()
    try:
        last = str(gate_function(cc))
    except Exception as e:
        last = 'Error'
    
    # Get BIN information
    bin_data = get_bin_info(cc[:6])
    
    level = bin_data.get('level', 'Unknown')
    brand = bin_data.get('brand', 'Unknown')
    card_type = bin_data.get('type', 'Unknown')
    country = bin_data.get('country', 'Unknown')
    country_flag = bin_data.get('country_flag', '🇺🇸')
    bank = bin_data.get('bank', 'Unknown')
        
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Determine message based on response
    if any(x in last.lower() for x in ['approved', 'success', 'live', 'funds available', 'authenticate attempt successful']):
        status_emoji = "✅"
        status_text = "Approved"
    elif any(x in last.lower() for x in ['declined', 'die', 'authentication failed', 'authenticate frictionless failed']):
        status_emoji = "❌"
        status_text = "Declined"
    else:
        status_emoji = "⚠️"
        status_text = "Unknown"
    
    msg = f'''<b>{status_emoji} {status_text}

⸙ Card ➼ <code>{cc}</code>
⸙ Response ➼ {last}
⸙ Gateway ➼ {gate_name}		
⸙ Bin Info ➼ {cc[:6]} - {card_type} - {brand} - {level}
⸙ Country ➼ {country} - {country_flag} 
⸙ Issuer ➼ <code>{bank}</code>
⸙ Time ➼ {"{:.1f}".format(execution_time)}s
⸙ Plan ➼ {plan_status}
⸙ Bot By: @Akira_fate</b>'''
    
    bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text=msg, parse_mode="HTML")

@bot.message_handler(content_types=["document"])
def main(message):
    name = message.from_user.first_name
    user_id = message.from_user.id
    
    # Check subscription
    has_sub, plan_status = check_subscription(user_id)
    if not has_sub:
        if plan_status == "FREE":
            keyboard = types.InlineKeyboardMarkup()
            ahmed = types.InlineKeyboardButton(text="✨ OWNER ✨", url="https://t.me/Outcome9k")
            contact_button = types.InlineKeyboardButton(text="✨ CHANNEL ✨", url="https://t.me/Outcome9k")
            keyboard.add(contact_button, ahmed)
            bot.send_message(chat_id=message.chat.id, text=f'''<b>HELLO {name}
THIS PARTICULAR BOT IS NOT FREE 
IF YOU WANT TO USE IT, YOU MUST PURCHASE A WEEKLY OR MONTHLY SUBSCRIPTION 

YOUR PLAN NOW {plan_status}</b>''', reply_markup=keyboard)
        else:
            bot.reply_to(message, '''<b>You Cannot Use The Bot Because Your Subscription Has Expired</b>''')
        return
        
    keyboard = types.InlineKeyboardMarkup()
    contact_button = types.InlineKeyboardButton(text=f"🏴‍☠️ BRAINTREE AUTH 🏴‍☠️", callback_data='br')
    sw = types.InlineKeyboardButton(text=f" STRIPE CHARGE 🪽", callback_data='str')
    keyboard.add(contact_button)
    keyboard.add(sw)
    bot.reply_to(message, text=f'<b>Choose The Gateway You Want To Use</b>', reply_markup=keyboard, parse_mode="HTML")
    ee = bot.download_file(bot.get_file(message.document.file_id).file_path)
    with open("combo.txt", "wb") as w:
        w.write(ee)

@bot.callback_query_handler(func=lambda call: call.data == 'str')
def stripe_callback(call):
    def my_function():
        id = call.from_user.id
        gate = 'Stripe Charge'
        dd = 0
        live = 0
        ch = 0
        ccnn = 0
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Checking Your Cards...⌛")
        try:
            with open("combo.txt", 'r') as file:
                lino = file.readlines()
                total = len(lino)
                try:
                    stopuser[f'{id}']['status'] = 'start'
                except:
                    stopuser[f'{id}'] = {
                        'status': 'start'
                    }
                    
                for cc in lino:
                    cc = cc.strip()
                    if not cc:
                        continue
                        
                    if stopuser[f'{id}']['status'] == 'stop':
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='STOPPED ✅\nCHANNEL BY ➜ @Akira_fate')
                        return
                    
                    # Use our BIN info function
                    bin_data = get_bin_info(cc[:6])
                    
                    level = bin_data.get('level', 'unknown')
                    bank = bin_data.get('bank', 'unknown')
                    country_flag = bin_data.get('country_flag', '🇺🇸')
                    country = bin_data.get('country', 'unknown')
                    brand = bin_data.get('brand', 'unknown')
                    card_type = bin_data.get('type', 'unknown')
                    
                    start_time = time.time()
                    try:
                        last = str(st(cc))
                    except Exception as e:
                        print(e)
                        last = "Website under maintenance"
                        
                    mes = types.InlineKeyboardMarkup(row_width=1)
                    cm1 = types.InlineKeyboardButton(f"• {cc} •", callback_data='u8')
                    status = types.InlineKeyboardButton(f"• STATUS ➜ {last} •", callback_data='u8')
                    cm3 = types.InlineKeyboardButton(f"• CHARGE ✅ ➜ [ {ch} ] •", callback_data='x')
                    ccn = types.InlineKeyboardButton(f"• CCN ☑️ ➜ [ {ccnn} ] •", callback_data='x')
                    cm4 = types.InlineKeyboardButton(f"• DECLINED ❌ ➜ [ {dd} ] •", callback_data='x')
                    risk = types.InlineKeyboardButton(f"• INSUFFICIENT FUNDS ☑️ ➜ [ {live} ] •", callback_data='x')
                    cm5 = types.InlineKeyboardButton(f"• TOTAL 👻 ➜ [ {total} ] •", callback_data='x')
                    stop = types.InlineKeyboardButton(f"[ STOP ]", callback_data='stop')
                    mes.add(cm1, status, cm3, ccn, risk, cm4, cm5, stop)
                    end_time = time.time()
                    execution_time = end_time - start_time
                    bot.edit_message_text(chat_id=call.message.chat.id, 
                      message_id=call.message.message_id, 
                      text=f'''Please Wait While Your Cards Are Being Checked At The Gateway {gate}
Bot By @Akira_fate''', reply_markup=mes)

                    msg = f'''<b>CHARGE ✅
- - - - - - - - - - - - - - - - - - - - - - -
◆ CARD ➜ <code>{cc}</code>
◆ GATEWAY ➜ {gate}
◆ RESPONSE ➜ {last}
- - - - - - - - - - - - - - - - - - - - - - -
◆ BIN ➜ <code>{cc[:6]} - {card_type} - {brand}</code>
◆ BANK ➜ <code>{bank}</code>
◆ COUNTRY ➜ <code>{country} - {country_flag}</code> 
- - - - - - - - - - - - - - - - - - - - - - -
◆ BY: @Akira_fate
◆ TAKEN ➜ {"{:.1f}".format(execution_time)} seconds .</b>'''
                    
                    if 'success' in last:
                        ch += 1
                        bot.send_message(call.from_user.id, msg, parse_mode="HTML")
                    elif "declined" in last:
                        dd += 1
                    
                    time.sleep(1)
        except Exception as e:
            print(e)
        stopuser[f'{id}']['status'] = 'start'
        bot.edit_message_text(chat_id=call.message.chat.id, 
                      message_id=call.message.message_id, 
                      text='BEEN COMPLETED ✅\nCHANNEL BY ➜ @Akira_fate')
    my_thread = threading.Thread(target=my_function)
    my_thread.start()

@bot.callback_query_handler(func=lambda call: call.data == 'br')
def braintree_callback(call):
    def my_function():
        id = call.from_user.id
        gate = 'Braintree Auth'
        dd = 0
        live = 0
        riskk = 0
        ccnn = 0
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Checking Your Cards...⌛")
        try:
            with open("combo.txt", 'r') as file:
                lino = file.readlines()
                total = len(lino)
                try:
                    stopuser[f'{id}']['status'] = 'start'
                except:
                    stopuser[f'{id}'] = {
                        'status': 'start'
                    }
                    
                for cc in lino:
                    cc = cc.strip()
                    if not cc:
                        continue
                        
                    if stopuser[f'{id}']['status'] == 'stop':
                        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='STOPPED ✅\nCHANNEL BY ➜ @Akira_fate')
                        return
                    
                    # Use our BIN info function
                    bin_data = get_bin_info(cc[:6])
                    
                    level = bin_data.get('level', 'unknown')
                    bank = bin_data.get('bank', 'unknown')
                    country_flag = bin_data.get('country_flag', '🇺🇸')
                    country = bin_data.get('country', 'unknown')
                    brand = bin_data.get('brand', 'unknown')
                    card_type = bin_data.get('type', 'unknown')
                    
                    start_time = time.time()
                    try:
                        last = str(Tele(cc))
                    except Exception as e:
                        print(e)
                        last = "ERROR"
                        
                    mes = types.InlineKeyboardMarkup(row_width=1)
                    cm1 = types.InlineKeyboardButton(f"• {cc} •", callback_data='u8')
                    status = types.InlineKeyboardButton(f"• STATUS ➜ {last} •", callback_data='u8')
                    cm3 = types.InlineKeyboardButton(f"• APPROVED ✅ ➜ [ {live} ] •", callback_data='x')
                    ccn = types.InlineKeyboardButton(f"• CCN ☑️ ➜ [ {ccnn} ] •", callback_data='x')
                    cm4 = types.InlineKeyboardButton(f"• DECLINED ❌ ➜ [ {dd} ] •", callback_data='x')
                    risk = types.InlineKeyboardButton(f"• RISK 🏴‍☠️ ➜ [ {riskk} ] •", callback_data='x')
                    cm5 = types.InlineKeyboardButton(f"• TOTAL 👻 ➜ [ {total} ] •", callback_data='x')
                    stop = types.InlineKeyboardButton(f"[ STOP ]", callback_data='stop')
                    mes.add(cm1, status, cm3, ccn, risk, cm4, cm5, stop)
                    end_time = time.time()
                    execution_time = end_time - start_time
                    bot.edit_message_text(chat_id=call.message.chat.id, 
                      message_id=call.message.message_id, 
                      text=f'''Please Wait While Your Cards Are Being Checked At The Gateway {gate}
Bot By @Akira_fate''', reply_markup=mes)
                    
                    msg = f'''<b>Approved ✅
            
Card ➼ <code>{cc}</code>
Response ➼ {last}
Gateway ➼ {gate}		
Country ➼ <code>{country} - {country_flag}</code> 
Bin ➼ <code>{cc[:6]} - {card_type} - {brand}</code>
Issuer ➼ <code>{bank}</code>
Time ➼ {"{:.1f}".format(execution_time)}
Bot By: @Akira_fate</b>'''

                    if "Approved" in last:
                        live += 1
                        bot.send_message(call.from_user.id, msg, parse_mode="HTML")
                    elif "Declined" in last:
                        dd += 1
                    
                    time.sleep(1)
        except Exception as e:
            print(e)
        stopuser[f'{id}']['status'] = 'start'
        bot.edit_message_text(chat_id=call.message.chat.id, 
                      message_id=call.message.message_id, 
                      text='BEEN COMPLETED ✅\nCHANNEL BY ➜ @Akira_fate')
    my_thread = threading.Thread(target=my_function)
    my_thread.start()

@bot.callback_query_handler(func=lambda call: call.data == 'stop')
def stop_callback(call):
    id = call.from_user.id
    if f'{id}' in stopuser:
        stopuser[f'{id}']['status'] = 'stop'
    bot.edit_message_text(chat_id=call.message.chat.id, 
                         message_id=call.message.message_id, 
                         text='STOPPED ✅\nCHANNEL BY ➜ @Akira_fate')

print("Bot started successfully")
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Error occurred: {e}")
    time.sleep(0)
