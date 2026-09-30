"""
=============================================================================
*  Project: Konkur PDF Hunter 🎓 (MONSTER EDITION 🦖)
*  Author: mm.keshavarzz | Supercharged by Senior AI 👨‍💻
*  Features:
*    - 2000-Message Deep Scan (شخم زدن ۲۰۰۰ پیام آخر بدون توقف) 📚
*    - Mathematical Anti-Pin (خنثی‌سازی تله پین‌مسیج با علم آمار) 🧮
*    - Smart Date Filter (جدا کردن فایل‌های ۷ روز اخیر) ⏳
=============================================================================
"""

import os
import re
import time
import statistics
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone

# لیست کانال‌ها
CHANNELS = [
    "Soal75", "WWW_AZMON_COM", "pdf_konkor", "www_book_com", 
    "Irdaneshamoz", "NOTRUPHIL", "ketabkonkuor", "plasma_ir", 
    "silent_konkor", "Vidana_file", "mrkonkor", "AyandehSazan_Ed"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

TAGS_DICTIONARY = {
    "رشته": {
        "🧬 تجربی": ["تجربی", "تجر", "biology_major"],
        "📐 ریاضی": ["ریاضی", "ریاضیات", "ریاض"],
        "⚖️ انسانی": ["انسانی", "فلسفه", "ادبیات_تخصصی"]
    },
    "آزمون": {
        "سراسری": ["سراسری", "کنکور", "konkur"],
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
        "ریاضیات": ["حسابان", "هندسه", "گسسته", "آمار", "ریاضی"],
        "عمومی/انسانی": ["ادبیات", "فارسی", "عربی", "دینی", "زبان", "اقتصاد", "منطق"]
    }
}

def extract_tags(text: str):
    clean_text = re.sub(r'[_#\-\u200c]', '', text.lower())
    found_tags = {"رشته": [], "آزمون": [], "درس": []}
    for category, items in TAGS_DICTIONARY.items():
        for tag_name, keywords in items.items():
            if any(kw in clean_text for kw in keywords):
                found_tags[category].append(tag_name)
    return found_tags

def send_to_telegram(file_title, post_url, tags, source_channel):
    bot_token = os.environ.get("TELEGRAM_TOKEN")
    channel_id = os.environ.get("TELEGRAM_CHANNEL")
    if not bot_token or not channel_id:
        return

    # 🎨 دیزاین خفن و لاکچری پیام‌ها
    reshteh = f"🎓 <b>رشته:</b> {' | '.join(tags['رشته'])}" if tags['رشته'] else ""
    azmoon = f"📝 <b>آزمون:</b> {' | '.join(tags['آزمون'])}" if tags['آزمون'] else ""
    dars = f"📚 <b>درس:</b> {' | '.join(tags['درس'])}" if tags['درس'] else ""
    
    details = "\n".join(filter(None, [reshteh, azmoon, dars]))
    if details:
        details = f"\n{details}\n"

    msg = (
        f"🧨 <b>شکار جدید توربین!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📄 <b>عنوان فایل:</b>\n"
        f"<blockquote>{file_title}</blockquote>\n"
        f"{details}"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"📡 <b>منبع:</b> @{source_channel}\n"
        f"📥 <a href='{post_url}'>[ ☁️ دانلود مستقیم فایل ]</a>"
    )

    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": channel_id, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": True}
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"❌ خطا در ارسال به تلگرام: {e}")

def main():
    print("🦖 هیولای توربین روشن شد! هدف: شخم زدن ۲۰۰۰ پیام آخر هر کانال...")
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    session = requests.Session()
    session.headers.update(HEADERS)

    for ch in CHANNELS:
        ch = ch.replace('@', '')
        print(f"\n🚜 در حال شخم زدن عمیق کانال: @{ch}")
        base_url = f"https://t.me/s/{ch}"
        current_url = base_url
        
        keep_scraping = True
        pages_scraped = 0
        total_files_in_channel = 0
        MAX_PAGES = 100 # 100 صفحه * 20 پیام = حدود 2000 پیام! 🤯

        while keep_scraping and pages_scraped < MAX_PAGES:
            try:
                res = session.get(current_url, timeout=15)
                if res.status_code == 503:
                    print("⚠️ تلگرام خسته شد (ارور 503)! 10 ثانیه استراحت تاکتیکی...")
                    time.sleep(10)
                    continue
                if res.status_code != 200:
                    break
                    
                soup = BeautifulSoup(res.text, 'html.parser')
                messages = soup.find_all('div', class_='tgme_widget_message')
                if not messages:
                    break

                valid_ids = []

                for msg in messages:
                    # ۱. گرفتن آیدی پیام برای ورق زدن
                    post_id_str = msg.get('data-post')
                    if post_id_str:
                        try: valid_ids.append(int(post_id_str.split('/')[-1]))
                        except: pass

                    # ۲. بررسی تاریخ پیام
                    time_tag = msg.find('time', class_='time')
                    post_time = None
                    if time_tag:
                        try: post_time = datetime.fromisoformat(time_tag.get('datetime'))
                        except: pass

                    # فیلتر جادویی ۷ روز اخیر
                    if not post_time or post_time < week_ago:
                        continue

                    # ۳. شکار PDF
                    doc_wrap = msg.find('div', class_='tgme_widget_message_document')
                    if doc_wrap:
                        title_elem = doc_wrap.find('div', class_='tgme_widget_message_document_title')
                        if not title_elem: continue
                        title = title_elem.text.strip()
                        
                        if title.lower().endswith('.pdf'):
                            post_url = f"https://t.me/{post_id_str}"
                            caption_elem = msg.find('div', class_='tgme_widget_message_text')
                            caption = caption_elem.text if caption_elem else ""
                            
                            tags = extract_tags(title + " " + caption)
                            send_to_telegram(title, post_url, tags, ch)
                            total_files_in_channel += 1
                            time.sleep(1.5)

                # ۴. الگوریتم جدید و هوشمند ضد تله پین‌مسیج (استفاده از میانه آماری)
                if valid_ids:
                    # گرفتن میانه (عدد وسط) برای حذف داده‌های پرت (پیام‌های پین‌شده خیلی جدید یا خیلی قدیمی)
                    median_id = statistics.median(valid_ids)
                    
                    # فقط آیدی‌هایی رو قبول می‌کنیم که با میانه اختلاف فاحش نداشته باشن
                    normal_ids = [vid for vid in valid_ids if abs(vid - median_id) < 3000]
                    
                    if not normal_ids:
                        normal_ids = valid_ids
                        
                    min_post_id = min(normal_ids)
                    
                    current_url = f"{base_url}?before={min_post_id}"
                    pages_scraped += 1
                    time.sleep(2)
                else:
                    break

            except Exception as e:
                print(f"❌ خطا در کانال @{ch}: {e}")
                break
        
        print(f"🎯 مجموع فایل‌های شکار شده از @{ch}: {total_files_in_channel} عدد (از بررسی ~{pages_scraped * 20} پیام)")

    print("\n🎉 عملیات هیولا تمام شد! خسته نباشی دلاور.")

if __name__ == "__main__":
    main()
