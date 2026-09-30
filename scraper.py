"""
=============================================================================
*  Project: Konkur PDF Hunter 🎓 (SMART ANTI-LOOP EDITION 🧠🥷)
*  Author: mm.keshavarzz | Supercharged by Senior AI 👨‍💻
*  Features:
*    - 🧠 No More Infinite Loops (حذف گرداب بازگشتی استارت‌های تکراری)
*    - 🎯 Guaranteed Button Click (کلیک تضمینی روی بررسی عضویت بر اساس متن دکمه)
*    - 🎒 Global Delayed Cleanup (خروج یکجا از همه کانال‌ها فقط در انتهای کار)
*    - 🛡️ Protector Shield Breaker (نفوذ به کانال‌های مخفی داخل واسطه‌ها)
*    - 🛑 Anti-PhoneTrap Shield (فرار هوشمند از تله ارسال شماره تلفن)
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
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors import UserAlreadyParticipantError, FloodWaitError

CHANNELS = [
    "Soal75", "WWW_AZMON_COM", "pdf_konkor", "www_book_com", 
    "Ireshamoz", "NOTRUPHIL", "ketabkonkuor", "plasma_ir", 
    "silent_konkor", "Via_file", "mrkonkor", "AyandehSazan_Ed"
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

# 🌐 دیتابیس‌های موقت در حافظه
SPONSOR_LINKS_ARCHIVE = set()
VISITED_BOT_PARAMS = set() 
GLOBAL_JOINED_CHANNELS = set() # کوله‌پشتی برای لفت دادن پایانی


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

async def try_join_private_link(client, link, depth_str=""):
    """نفوذ به کانال‌ها و گپ‌های خصوصی"""
    priv_match = re.search(r't\.me/(?:\+|joinchat/)([a-zA-Z0-9_-]+)', link)
    if priv_match:
        inv_hash = priv_match.group(1)
        try:
            res = await client(ImportChatInviteRequest(inv_hash))
            if hasattr(res, 'chats') and res.chats:
                ch_id = res.chats[0].id
                GLOBAL_JOINED_CHANNELS.add(ch_id)
                print(f"{depth_str}🥷 نفوذ موفق به کانال پرایوت اسپانسر!")
            await asyncio.sleep(2)
        except UserAlreadyParticipantError:
            pass
        except FloodWaitError as e:
            print(f"{depth_str}🛑 فلود ویت در جوین: {e.seconds} ثانیه...")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"{depth_str}⚠️ خطا در ورود به لینک پرایوت: {e}")

async def handle_bot_interaction(client, bot_username, start_param, source_channel, source_post_id, depth=1):
    """مدیریت هوشمندانه ربات بدون گیج شدن و لوپ زدن"""
    global SPONSOR_LINKS_ARCHIVE, VISITED_BOT_PARAMS, GLOBAL_JOINED_CHANNELS
    
    unique_id = f"{bot_username}_{start_param}"
    if unique_id in VISITED_BOT_PARAMS:
        return
        
    VISITED_BOT_PARAMS.add(unique_id)
    print(f"\n{'  '*depth}🤖 اعزام به ربات: @{bot_username} با پارامتر: {start_param}")
    
    try:
        # ۱. ارسال فقط یک استارت
        try:
            sent_msg = await client.send_message(bot_username, f"/start {start_param}")
        except FloodWaitError as e:
            if e.seconds < 45:
                await asyncio.sleep(e.seconds + 2)
                sent_msg = await client.send_message(bot_username, f"/start {start_param}")
            else:
                return

        # ۲. صبر منطقی برای پاسخ ربات
        await asyncio.sleep(4) 

        bot_response = None
        async for m in client.iter_messages(bot_username, limit=3):
            if m.id != sent_msg.id:
                bot_response = m
                break

        if not bot_response:
            print(f"{'  '*depth}⚠️ ربات جوابی نداد!")
            return

        text = bot_response.text or ""
        if any(w in text for w in ["شماره", "احراز هویت", "ارسال شماره", "phone", "مخاطب"]):
            print(f"{'  '*depth}🛑 تله شماره تلفن! اسکیپ شد.")
            return

        # ۳. عضویت در کانال‌های اسپانسر (بدون رفتن به اسکن‌های بی‌پایان!)
        verify_btn_text = None
        verify_coords = None

        if bot_response.reply_markup and hasattr(bot_response.reply_markup, 'rows'):
            for row_idx, row in enumerate(bot_response.reply_markup.rows):
                for col_idx, btn in enumerate(row.buttons):
                    # اگه دکمه حاوی لینک بود (اسپانسرها)
                    if hasattr(btn, 'url') and btn.url:
                        SPONSOR_LINKS_ARCHIVE.add(btn.url)
                        priv_match = re.search(r't\.me/(?:\+|joinchat/)([a-zA-Z0-9_-]+)', btn.url)
                        pub_match = re.search(r't\.me/([a-zA-Z0-9_]+)$', btn.url)

                        try:
                            if priv_match:
                                await try_join_private_link(client, btn.url, '  '*depth)
                            elif pub_match:
                                target_c = pub_match.group(1)
                                if not target_c.lower().endswith('bot'):
                                    await client(JoinChannelRequest(target_c))
                                    GLOBAL_JOINED_CHANNELS.add(target_c)
                                    print(f"{'  '*depth}📢 عضو اسپانسر شدیم: @{target_c}")
                                    await asyncio.sleep(2)
                        except UserAlreadyParticipantError:
                            pass
                        except Exception as e:
                            print(f"{'  '*depth}⚠️ خطای عضویت اسپانسر: {e}")

                    # پیدا کردن دکمه بررسی / تایید
                    btn_text = getattr(btn, 'text', '')
                    if any(kw in btn_text for kw in ["بررسی", "تایید", "عضو شدم", "دریافت"]):
                        verify_btn_text = btn_text
                        verify_coords = (row_idx, col_idx)

            # ۴. فشردن قطعی و تضمینی دکمه «بررسی عضویت»
            if verify_btn_text or verify_coords:
                print(f"{'  '*depth}🔘 همه کانال‌ها عضو شد؛ فشردن «{verify_btn_text or 'بررسی'}»...")
                await asyncio.sleep(2)
                try:
                    # روش اول: کلیک مستقیم متنی (بسیار پایدارتر در ربات‌های ایرانی)
                    if verify_btn_text:
                        await asyncio.wait_for(bot_response.click(text=verify_btn_text), timeout=10.0)
                    else:
                        await asyncio.wait_for(bot_response.click(verify_coords[0], verify_coords[1]), timeout=10.0)
                except Exception as click_err:
                    print(f"{'  '*depth}⚠️ تلاش دوم کلیک با ایندکس...")
                    try:
                        if verify_coords:
                            await bot_response.click(verify_coords[0], verify_coords[1])
                    except Exception as e:
                        print(f"{'  '*depth}❌ کلیک نشد: {e}")

                # صبر حیاتی تا ربات استعلام بگیره و پیام فایل رو رها کنه
                print(f"{'  '*depth}⏳ ۶ ثانیه انتظار برای تحویل پی‌دی‌اف...")
                await asyncio.sleep(6)

        # ۵. دریافت فایل یا لینک دانلود از ربات
        file_found = False
        async for bot_msg in client.iter_messages(bot_username, limit=3):
            if bot_msg.document and bot_msg.document.mime_type == 'application/pdf':
                b_file = "فایل_کنکوری.pdf"
                for attr in bot_msg.document.attributes:
                    if isinstance(attr, DocumentAttributeFilename) and attr.file_name:
                        b_file = attr.file_name
                
                print(f"{'  '*depth}🎉 شکار شدددد! فایل رو گرفتیم: {b_file}")
                if TARGET_CHANNEL:
                    await client.forward_messages(TARGET_CHANNEL, bot_msg)
                
                post_url = f"https://t.me/{source_channel}/{source_post_id}"
                tags = extract_tags(b_file + " " + (bot_msg.text or ""))
                send_to_telegram(b_file, post_url, tags, f"{source_channel} (از چنگ @{bot_username})")
                file_found = True
                break
            
            elif bot_msg.text and bot_msg.id != sent_msg.id:
                 text_links = re.findall(r'(https?://t\.me/[^\s]+)', bot_msg.text)
                 for link in text_links:
                    if not "start=" in link:
                        tags = extract_tags(bot_msg.text)
                        send_to_telegram("لینک دانلود مستقیم", link, tags, f"ربات @{bot_username}")
                        file_found = True
                        break
                 if file_found:
                     break

        if not file_found:
            print(f"{'  '*depth}❌ فایل تحویل داده نشد (شاید یکی از کانال‌ها تایید نشده).")

    except Exception as e:
        print(f"{'  '*depth}⚠️ خطا در پردازش: {e}")


async def cleanup_all_joined_channels(client):
    """خروج شیک و باوقار از همه کانال‌ها فقط وقتی که کار کل برنامه تموم شد"""
    global GLOBAL_JOINED_CHANNELS
    if not GLOBAL_JOINED_CHANNELS:
        print("🧹 هیچ کانال اسپانسری در لیست خروج وجود ندارد.")
        return
        
    print(f"\n🚪 شروع پاکسازی سراسری: در حال خروج از {len(GLOBAL_JOINED_CHANNELS)} کانال...")
    for ch in list(GLOBAL_JOINED_CHANNELS):
        try:
            await client(LeaveChannelRequest(ch))
            print(f"👋 با موفقیت لفت داده شد از: {ch}")
            await asyncio.sleep(2)
        except FloodWaitError as e:
            print(f"🛑 فلود ویت در زمان خروج! {e.seconds} ثانیه...")
            await asyncio.sleep(e.seconds)
        except Exception:
            pass
            
    GLOBAL_JOINED_CHANNELS.clear()
    print("✨ اکانت کاملاً تمیز شد و هیچ کانال اضافه‌ای باقی نماند!")


async def main():
    print("🦖 شکارچی پی‌دی‌اف کنکور با مغز ارتقایافته روشن شد!")
    if not SESSION_STRING:
        print("❌ سشن استرینگ تلگرام یافت نشد!")
        return

    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.start()
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)

    try:
        for ch in CHANNELS:
            ch_clean = ch.replace('@', '')
            print(f"\n======================================")
            print(f"🚜 در حال بررسی کانال منبع: @{ch_clean}")
            print(f"======================================")

            try:
                # پیام‌های کانال رو بررسی می‌کنیم (با لیمیت معقول برای جلوگیری از اسپم)
                async for msg in client.iter_messages(ch_clean, limit=400):
                    if msg.date < week_ago:
                        break

                    # ۱. صید مستقیم فایل از خود کانال
                    if msg.document and msg.document.mime_type == 'application/pdf':
                        file_name = "فایل.pdf"
                        for attr in msg.document.attributes:
                            if isinstance(attr, DocumentAttributeFilename) and attr.file_name:
                                file_name = attr.file_name
                        
                        tags = extract_tags(file_name + " " + (msg.text or ""))
                        post_url = f"https://t.me/{ch_clean}/{msg.id}"
                        send_to_telegram(file_name, post_url, tags, ch_clean)
                        continue

                    # ۲. استخراج لینک‌های ربات واسطه
                    search_text = msg.text or ""
                    if msg.reply_markup and hasattr(msg.reply_markup, 'rows'):
                        for row in msg.reply_markup.rows:
                            for btn in row.buttons:
                                if hasattr(btn, 'url') and btn.url:
                                    search_text += f" {btn.url} "

                    bot_links = re.findall(r't\.me/([a-zA-Z0-9_]+)\?start=([a-zA-Z0-9_-]+)', search_text)
                    for b_user, s_param in bot_links:
                        # هر فایل رو می‌گیره و تموم می‌کنه، بدون اینکه بیفته توی لوپ
                        await handle_bot_interaction(client, b_user, s_param, ch_clean, msg.id, depth=1)
                        # مکث ۳ ثانیه‌ای بین استارت‌ها مثل رفتار واقعی انسان
                        await asyncio.sleep(3)

            except Exception as e:
                print(f"❌ خطا در کانال @{ch_clean}: {e}")

        # ذخیره فایل آرشیو لینک‌ها در پایان
        if SPONSOR_LINKS_ARCHIVE:
            os.makedirs("channels", exist_ok=True)
            today_str = datetime.now().strftime("%Y-%m-%d")
            file_path = os.path.join("channels", f"sponsor_links_{today_str}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                for link in sorted(SPONSOR_LINKS_ARCHIVE):
                    f.write(link + "\n")
            print(f"\n📁 {len(SPONSOR_LINKS_ARCHIVE)} لینک اسپانسر در {file_path} آرشیو شد.")

        print("\n🏁 تمام کانال‌ها و فایل‌ها بررسی شدند.")

    finally:
        # 🧼 حالا که همه فایل‌ها جمع‌آوری شد، دستور لفت دادن سراسری اجرا میشه!
        await cleanup_all_joined_channels(client)


if __name__ == "__main__":
    asyncio.run(main())
