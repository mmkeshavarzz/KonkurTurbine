"""
=============================================================================
*  Project: Konkur PDF Hunter 🎓 (TELETHON MONSTER EDITION 🦖)
*  Author: mm.keshavarzz | Supercharged by Senior AI 👨‍💻
*  Features:
*    - Async Userbot Architecture (یوزربات فوق‌سریع) ⚡
*    - Bot-in-Bot Bypass (دور زدن ربات‌های واسطه و سرقت PDF مخفی) 🥷
*    - Perfect Chronological Scan (بدون افتادن در تله پین‌مسیج) 🕰️
*    - Smart Date Filter (فیلتر دقیق ۷ روز اخیر) ⏳
=============================================================================
"""

import os
import re
import asyncio
import requests
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import DocumentAttributeFilename

# لیست کانال‌ها
CHANNELS = [
    "Soal75", "WWW_AZMON_COM", "pdf_konkor", "www_book_com", 
    "Irdaneshamoz", "NOTRUPHIL", "ketabkonkuor", "plasma_ir", 
    "silent_konkor", "Vidana_file", "mrkonkor", "AyandehSazan_Ed"
]

# دیتابیس کلمات کلیدی
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

# گرفتن سکرت‌ها از محیط سیستم (GitHub Secrets)
API_ID = int(os.environ.get("TELEGRAM_API_ID", 2040))
API_HASH = os.environ.get("TELEGRAM_API_HASH", "")
SESSION_STRING = os.environ.get("TELEGRAM_SESSION", "")
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TARGET_CHANNEL = os.environ.get("TELEGRAM_CHANNEL", "")

def extract_tags(text: str):
    """ استخراج هوشمند تگ‌ها از متن """
    clean_text = re.sub(r'[_#\-\u200c]', '', text.lower())
    found_tags = {"رشته": [], "آزمون": [], "درس": []}
    for category, items in TAGS_DICTIONARY.items():
        for tag_name, keywords in items.items():
            if any(kw in clean_text for kw in keywords):
                found_tags[category].append(tag_name)
    return found_tags

def send_to_telegram(file_title, post_url, tags, source_channel):
    """ ارسال بنر گرافیکی به کانال از طریق ربات API """
    if not BOT_TOKEN or not TARGET_CHANNEL:
        return

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
        f"📥 <a href='{post_url}'>[ ☁️ مشاهده/دانلود فایل ]</a>"
    )

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TARGET_CHANNEL, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": True}
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"❌ خطا در ارسال بنر: {e}")

async def extract_bot_links(msg):
    """ پیدا کردن لینک ربات‌های واسطه در متن یا دکمه‌های شیشه‌ای """
    links = []
    search_text = msg.text or ""
    # جستجو در دکمه‌های زیر پیام
    if msg.reply_markup and hasattr(msg.reply_markup, 'rows'):
        for row in msg.reply_markup.rows:
            for btn in row.buttons:
                if hasattr(btn, 'url') and btn.url:
                    search_text += f" {btn.url} "
                    
    # استخراج فرمت t.me/BotName?start=123
    found = re.findall(r't\.me/([a-zA-Z0-9_]+)\?start=([a-zA-Z0-9_-]+)', search_text)
    links.extend(found)
    return links

async def main():
    print("🦖 موتور یوزربات توربین با قدرت Telethon روشن شد!")
    if not SESSION_STRING:
        print("❌ واویلا! سشن استرینگ پیدا نشد. حتما توی گیت‌هاب سکرت‌ها اضافه‌اش کن.")
        return

    # استارت کلاینت یوزربات
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.start()
    
    # فیلتر تاریخ (دقیقاً ۷ روز گذشته)
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)

    for ch in CHANNELS:
        ch_clean = ch.replace('@', '')
        print(f"\n🚜 در حال شخم زدن کانال: @{ch_clean} ...")
        total_files = 0
        scanned_msgs = 0

        try:
            # اسکن 2000 پیام آخر (اتوماتیک از جدید به قدیم)
            async for msg in client.iter_messages(ch_clean, limit=2000):
                # اگر رسیدیم به پیام‌های قدیمی‌تر از 7 روز، این کانال رو بی‌خیال شو
                if msg.date < week_ago:
                    break 
                
                scanned_msgs += 1
                is_pdf = False
                file_title = "فایل_بدون_نام.pdf"

                # ----------------------------------------------------
                # شکار نوع اول: فایل PDF مستقیم
                # ----------------------------------------------------
                if msg.document:
                    if msg.document.mime_type == 'application/pdf':
                        is_pdf = True
                    # پیدا کردن اسم دقیق فایل
                    for attr in msg.document.attributes:
                        if isinstance(attr, DocumentAttributeFilename) and attr.file_name:
                            file_title = attr.file_name
                            if file_title.lower().endswith('.pdf'):
                                is_pdf = True
                    
                    if is_pdf:
                        caption = msg.text or ""
                        tags = extract_tags(file_title + " " + caption)
                        post_url = f"https://t.me/{ch_clean}/{msg.id}"
                        send_to_telegram(file_title, post_url, tags, ch_clean)
                        total_files += 1
                        continue # برو پیام بعدی

                # ----------------------------------------------------
                # شکار نوع دوم: دور زدن ربات‌های واسطه (Bot-in-Bot) 🥷
                # ----------------------------------------------------
                bot_links = await extract_bot_links(msg)
                for bot_username, start_param in bot_links:
                    print(f"🕵️‍♂️ ربات واسطه کشف شد! ارسال دستور حمله به @{bot_username}")
                    try:
                        # ارسال دستور استارت به ربات واسطه
                        await client.send_message(bot_username, f"/start {start_param}")
                        await asyncio.sleep(4) # 4 ثانیه صبر برای دریافت جواب از ربات
                        
                        # خوندن آخرین پیام ربات واسطه
                        async for bot_msg in client.iter_messages(bot_username, limit=2):
                            if bot_msg.document and bot_msg.document.mime_type == 'application/pdf':
                                b_file = "فایل_مخفی.pdf"
                                for attr in bot_msg.document.attributes:
                                    if isinstance(attr, DocumentAttributeFilename) and attr.file_name:
                                        b_file = attr.file_name
                                
                                # فوروارد کردن خود فایل مخفی به کانال تارگت! 🚀
                                if TARGET_CHANNEL:
                                    await client.forward_messages(TARGET_CHANNEL, bot_msg)
                                
                                # ارسال بنر گرافیکی
                                tags = extract_tags(b_file + " " + (bot_msg.text or msg.text or ""))
                                post_url = f"https://t.me/{ch_clean}/{msg.id}"
                                send_to_telegram(b_file, post_url, tags, f"{ch_clean} (ربات واسطه)")
                                total_files += 1
                                break
                    except Exception as e:
                        print(f"⚠️ ربات واسطه @{bot_username} مقاومت کرد: {e}")

                await asyncio.sleep(0.5) # استراحت کوچیک برای جلوگیری از بن شدن یوزربات

        except Exception as e:
            print(f"❌ خطا در کانال @{ch_clean}: {e}")
        
        print(f"🎯 نتیجه @{ch_clean}: کشف {total_files} فایل (از بین {scanned_msgs} پیام اسکن شده)")

    print("\n🎉 عملیات هیولای Telethon تمام شد! خسته نباشی دلاور.")

if __name__ == "__main__":
    asyncio.run(main())
