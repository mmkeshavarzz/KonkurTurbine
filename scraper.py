"""
=============================================================================
*  Project: Konkur PDF Hunter & Auto Categorizer 🎓 (Turbine Style)
*  Author: mm.keshavarzz | Cleaned & Supercharged by Senior Dev 👨‍💻
*  Features:
*    - Time-Travel Filtering (Only 7-Days Old Files) ⏳
*    - Smart Regex Categorization (Majors, Exams, Lessons) 🧠
*    - Hashtag & Attached-words bypass mechanism
*    - 🚀 Auto-Broadcast to Telegram Channel!
=============================================================================
"""

import os
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone

# =============================================================================
# 📡 لیست کانال‌های هدف (بدون @)
# =============================================================================
CHANNELS = [
    "Soal75", "WWW_AZMON_COM", "pdf_konkor", "www_book_com", "Irdaneshamoz", "NOTRUPHIL", "@ketabkonkuor",  # نمونه - کانال‌های خودت رو اینجا بذار
    "plasma_ir", "silent_konkor", "Vidana_file", "mrkonkor", "AyandehSazan_Ed"
    
    
    
    
    # "channel_name_1", "channel_name_2"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# =============================================================================
# 🏷️ دیکشنری دسته‌بندی هوشمند (تشخیص هشتگ و کلمات چسبیده)
# =============================================================================
TAGS_DICTIONARY = {
    "رشته": {
        "🧬 تجربی": ["تجربی", "تجر", "biology_major"],
        "📐 ریاضی": ["ریاضی", "ریاضیات", "ریاض"],
        "⚖️ انسانی": ["انسانی", "فلسفه", "ادبیات_تخصصی"]
    },
    "آزمون": {
        "کنکور سراسری": ["سراسری", "کنکور", "konkur"],
        "قلم‌چی": ["قلم", "قلمچی", "قلم_چی", "کانون"],
        "ماز": ["ماز", "maz"],
        "گاج": ["گاج", "gaj"],
        "گزینه دو": ["گزینه", "گزینه۲", "گزینهدو", "گزینه_دو"],
        "آرمان": ["آرمان", "arman"],
        "زیستاز": ["زیستاز", "zistaz"],
        "دوپینگ": ["دوپینگ", "doping"],
        "خیلی سبز": ["خیلی_سبز", "خیلیسبز", "kheilisabz"]
    },
    "درس": {
        "زیست‌شناسی": ["زیست", "zist", "گیاهی", "جانوری"],
        "شیمی": ["شیمی", "shimi"],
        "فیزیک": ["فیزیک", "fizik"],
        "ریاضیات": ["حسابان", "هندسه", "گسسته", "آمار"],
        "دروس عمومی/انسانی": ["ادبیات", "فارسی", "عربی", "دینی", "زبان", "اقتصاد", "منطق", "فلسفه", "روانشناسی", "جامعه"]
    }
}

# =============================================================================
# 🧹 تابع تمیزکننده و تگ‌یاب (قاتل هشتگ‌ها و کلمات چسبیده)
# =============================================================================
def extract_tags(text: str):
    """متن رو می‌گیره، زیر و رو می‌کنه و تگ‌های مرتبط رو پیدا می‌کنه."""
    # حذف کاراکترهای اضافی مثل # و _ و فاصله‌های مجازی برای جستجوی بهتر
    clean_text = re.sub(r'[_#\-\u200c]', '', text.lower())
    
    found_tags = {"رشته": [], "آزمون": [], "درس": []}
    
    for category, items in TAGS_DICTIONARY.items():
        for tag_name, keywords in items.items():
            if any(kw in clean_text for kw in keywords):
                found_tags[category].append(tag_name)
                
    return found_tags

# =============================================================================
# ⏳ فیلتر زمان (ماشین زمان ۷ روزه)
# =============================================================================
def is_from_last_week(date_str: str) -> bool:
    """بررسی میکنه که آیا پست مال شنبه تا جمعه اخیر هست یا نه."""
    if not date_str:
        return False
    try:
        post_time = datetime.fromisoformat(date_str)
        now = datetime.now(timezone.utc)
        # فقط فایل‌هایی که در 7 روز گذشته آپلود شدن
        return (now - post_time) <= timedelta(days=7)
    except:
        return False

# =============================================================================
# 🚀 ارسال مستقیم به کانال تلگرام
# =============================================================================
def send_to_telegram(file_title, post_url, tags, source_channel):
    bot_token = os.environ.get("TELEGRAM_TOKEN")
    channel_id = os.environ.get("TELEGRAM_CHANNEL")

    if not bot_token or not channel_id:
        print("⚠️ توکن تلگرام یا آیدی کانال ست نشده!")
        return

    # ساخت پیام با کلاس و خوشگل
    msg = f"🎓 **فایل جدید شکار شد!**\n\n"
    msg += f"📄 **عنوان:** `{file_title}`\n\n"
    
    if tags['رشته']: msg += f"🎓 **رشته:** {' | '.join(tags['رشته'])}\n"
    if tags['آزمون']: msg += f"📝 **آزمون:** {' | '.join(tags['آزمون'])}\n"
    if tags['درس']: msg += f"📚 **درس:** {' | '.join(tags['درس'])}\n"
    
    msg += f"\n📢 **منبع:** `@{source_channel}`\n"
    msg += f"📥 **لینک دانلود مستقیم پست:**\n[کلیک کنید و فایل را دریافت کنید]({post_url})"

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": channel_id,
            "text": msg,
            "parse_mode": "Markdown",
            "disable_web_page_preview": True
        }
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"❌ خطا در ارسال فایل {file_title}: {e}")

# =============================================================================
# ⚙️ موتور اصلی (The Core)
# =============================================================================
def main():
    print("🕵️‍♂️ شکارچی کنکور روشن شد! در حال اسکن فایل‌های هفته اخیر...")
    
    for ch in CHANNELS:
        print(f"🔍 در حال بررسی کانال: @{ch}")
        try:
            res = requests.get(f"https://t.me/s/{ch}", headers=HEADERS, timeout=15)
            if res.status_code != 200:
                continue
                
            soup = BeautifulSoup(res.text, 'html.parser')
            messages = soup.find_all('div', class_='tgme_widget_message')
            
            for msg in messages:
                # 1. بررسی زمان
                time_tag = msg.find('time', class_='time')
                if not time_tag or not is_from_last_week(time_tag.get('datetime')):
                    continue # اگه مال این هفته نیست، بی‌خیالش شو!

                # 2. پیدا کردن داکیومنت (فایل)
                doc_wrap = msg.find('div', class_='tgme_widget_message_document')
                if doc_wrap:
                    title_elem = doc_wrap.find('div', class_='tgme_widget_message_document_title')
                    if not title_elem: continue
                    title = title_elem.text.strip()
                    
                    # اگه پی‌دی‌اف بود...
                    if title.lower().endswith('.pdf'):
                        post_id = msg.get('data-post') # فرمت: channel/123
                        post_url = f"https://t.me/{post_id}"
                        
                        # استخراج متن کپشن برای دسته‌بندی بهتر
                        caption_elem = msg.find('div', class_='tgme_widget_message_text')
                        caption = caption_elem.text if caption_elem else ""
                        
                        # جستجوی تگ‌ها در اسم فایل و کپشن
                        combined_text = title + " " + caption
                        tags = extract_tags(combined_text)
                        
                        # ارسال به کانال
                        send_to_telegram(title, post_url, tags, ch)
                        print(f"✅ ارسال شد: {title}")
                        time.sleep(2) # یه نفس کوچیک برای جلوگیری از بن شدن توسط تلگرام
                        
        except Exception as e:
            print(f"❌ خطا در اسکن کانال @{ch}: {e}")

    print("🎉 عملیات هفتگی با موفقیت به پایان رسید!")

if __name__ == "__main__":
    main()
