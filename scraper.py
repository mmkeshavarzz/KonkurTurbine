"""
=============================================================================
*  Project: Konkur PDF Hunter 🎓 (BYPASS FORCE-JOIN EDITION 🥷)
*  Author: mm.keshavarzz | Supercharged by Senior AI 👨‍💻
*  Features:
*    - Auto-Join Sponsor Channels (عضویت موقت در اسپانسرها) 📢
*    - Auto-Click Inline Buttons (زدن دکمه بررسی عضویت) 🔘
*    - Auto-Leave (لفت دادن سریع برای تمیز ماندن اکانت) 🧹
*    - Anti-PhoneTrap Shield (فرار از تله ارسال شماره تلفن) 🛡️
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
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest

CHANNELS = [
    "Soal75", "WWW_AZMON_COM", "pdf_konkor", "www_book_com", 
    "Irdaneshamoz", "NOTRUPHIL", "ketabkonkuor", "plasma_ir", 
    "silent_konkor", "Vidana_file", "mrkonkor", "AyandehSazan_Ed"
]

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

API_ID = int(os.environ.get("TELEGRAM_API_ID", 2040))
API_HASH = os.environ.get("TELEGRAM_API_HASH", "")
SESSION_STRING = os.environ.get("TELEGRAM_SESSION", "")
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TARGET_CHANNEL = os.environ.get("TELEGRAM_CHANNEL", "")

def extract_tags(text: str):
    clean_text = re.sub(r'[_#\-\u200c]', '', text.lower())
    found_tags = {"رشته": [], "آزمون": [], "درس": []}
    for category, items in TAGS_DICTIONARY.items():
        for tag_name, keywords in items.items():
            if any(kw in clean_text for kw in keywords):
                found_tags[category].append(tag_name)
    return found_tags

def send_to_telegram(file_title, post_url, tags, source_channel):
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

async def handle_bot_interaction(client, bot_username, start_param, source_channel, source_post_id):
    """ مدیریت هوشمند ربات‌های واسطه و دور زدن جوین اجباری """
    print(f"🤖 ارسال استارت به ربات واسطه: @{bot_username}")
    joined_channels = []
    
    try:
        # ارسال پیام استارت
        await client.send_message(bot_username, f"/start {start_param}")
        await asyncio.sleep(3)

        # دریافت پاسخ ربات
        bot_response = None
        async for m in client.iter_messages(bot_username, limit=1):
            bot_response = m
            break

        if not bot_response:
            return

        text = bot_response.text or ""
        
        # ⚠️ سپر امنیتی ۱: اگر ربات شماره موبایل خواست، سریع فرار کن!
        if any(w in text for w in ["شماره", "احراز هویت", "ارسال شماره", "phone", "مخاطب"]):
            print(f"🛑 هشدار امنیتی: ربات @{bot_username} درخواست شماره تلفن دارد! اسکیپ شد.")
            return

        # 📢 دور زدن قفل جوین اجباری (Force Join)
        if bot_response.reply_markup and hasattr(bot_response.reply_markup, 'rows'):
            verify_button = None
            
            # پیدا کردن کانال‌های اسپانسری و عضویت در آن‌ها
            for row in bot_response.reply_markup.rows:
                for btn in row.buttons:
                    # اگر لینک کانال باشد
                    if hasattr(btn, 'url') and btn.url:
                        ch_match = re.search(r't\.me/([a-zA-Z0-9_+]+)', btn.url)
                        if ch_match:
                            target_c = ch_match.group(1)
                            if not target_c.endswith('bot'):
                                try:
                                    print(f"➕ عضویت موقت در اسپانسر: {target_c}")
                                    await client(JoinChannelRequest(target_c))
                                    joined_channels.append(target_c)
                                    await asyncio.sleep(2) # وقفه برای جلوگیری از بن شدن
                                except Exception as e:
                                    print(f"نتوانست عضو {target_c} شود: {e}")
                    
                    # اگر دکمه "بررسی عضویت" یا "تایید" باشد
                    btn_text = getattr(btn, 'text', '')
                    if any(kw in btn_text for kw in ["بررسی", "تایید", "عضو شدم", "دریافت"]):
                        verify_button = btn

            # کلیک روی دکمه بررسی عضویت
            if verify_button and hasattr(verify_button, 'data'):
                print("🔘 فشردن دکمه بررسی عضویت...")
                await bot_response.click(data=verify_button.data)
                await asyncio.sleep(4)

        # خوندن پیام جدید بعد از تایید عضویت
        async for bot_msg in client.iter_messages(bot_username, limit=2):
            if bot_msg.document and bot_msg.document.mime_type == 'application/pdf':
                b_file = "فایل_مخفی.pdf"
                for attr in bot_msg.document.attributes:
                    if isinstance(attr, DocumentAttributeFilename) and attr.file_name:
                        b_file = attr.file_name
                
                print(f"🎯 فایل مخفی شکار شد: {b_file}")
                # فوروارد فایل به کانال خودت
                if TARGET_CHANNEL:
                    await client.forward_messages(TARGET_CHANNEL, bot_msg)
                
                post_url = f"https://t.me/{source_channel}/{source_post_id}"
                tags = extract_tags(b_file + " " + (bot_msg.text or ""))
                send_to_telegram(b_file, post_url, tags, f"{source_channel} (ربات {bot_username})")
                break

    except Exception as e:
        print(f"⚠️ خطای پردازش ربات واسطه: {e}")
    finally:
        # 🧹 پاکسازی: لفت دادن از تمام کانال‌های اسپانسری
        for c in joined_channels:
            try:
                print(f"➖ خروج خودکار از اسپانسر: {c}")
                await client(LeaveChannelRequest(c))
                await asyncio.sleep(1)
            except:
                pass

async def main():
    print("🦖 موتور پیشرفته توربین فعال شد!")
    if not SESSION_STRING:
        print("❌ سشن استرینگ وجود ندارد!")
        return

    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.start()
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)

    for ch in CHANNELS:
        ch_clean = ch.replace('@', '')
        print(f"\n🚜 شخم زدن: @{ch_clean}")

        try:
            async for msg in client.iter_messages(ch_clean, limit=1000):
                if msg.date < week_ago:
                    break

                # شکار مستقیم PDF
                if msg.document and msg.document.mime_type == 'application/pdf':
                    file_name = "فایل.pdf"
                    for attr in msg.document.attributes:
                        if isinstance(attr, DocumentAttributeFilename) and attr.file_name:
                            file_name = attr.file_name
                    
                    tags = extract_tags(file_name + " " + (msg.text or ""))
                    post_url = f"https://t.me/{ch_clean}/{msg.id}"
                    send_to_telegram(file_name, post_url, tags, ch_clean)
                    continue

                # شکار از طریق ربات واسطه
                search_text = msg.text or ""
                if msg.reply_markup and hasattr(msg.reply_markup, 'rows'):
                    for row in msg.reply_markup.rows:
                        for btn in row.buttons:
                            if hasattr(btn, 'url') and btn.url:
                                search_text += f" {btn.url} "

                bot_links = re.findall(r't\.me/([a-zA-Z0-9_]+)\?start=([a-zA-Z0-9_-]+)', search_text)
                for b_user, s_param in bot_links:
                    await handle_bot_interaction(client, b_user, s_param, ch_clean, msg.id)
                    await asyncio.sleep(2)

        except Exception as e:
            print(f"❌ خطا در کانال @{ch_clean}: {e}")

    print("\n🏁 اسکن به اتمام رسید.")

if __name__ == "__main__":
    asyncio.run(main())
