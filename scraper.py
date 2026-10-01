"""
=============================================================================
*  Project: Konkur PDF Hunter 🎓 (SMART ANTI-LOOP & CLICK FIX EDITION 🧠🥷)
*  Author: mm.keshavarzz | Supercharged by Senior AI 👨‍💻
*  Features:
*    - 🧠 No More Infinite Loops (حذف کامل گرداب بازگشتی استارت‌های تکراری)
*    - 🎯 Guaranteed Button Click (کلیک متنی و دقیق روی «بررسی عضویت»)
*    - 🎒 Global Delayed Cleanup (خروج یکجا از همه کانال‌ها فقط در انتهای کار)
*    - 🛡️ Protector Shield Breaker (پشتیبانی از لینک‌های پرایوت و جوین‌چت)
*    - 🛑 Anti-PhoneTrap Shield (فرار هوشمند از تله شماره تلفن)
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
    "silent_konkor", "Via_file", "mrkonkor", "AyandehSazan_Ed",
    "Pdfkonkorr", "kotob_land", "gozve_Darsi", "ziistkonkoor",
    "fiziikkonkoor", "shimiikonkoor", "shimiikonkoor", "riaziikonkor", 
    "konkurbartar3", "mrkonkor", "Konkor_Elite",
    "MafiaKetab", "KoroshKabir_bot", "Senatorjani_bot", "HYPEJOZVE_BOT", "mafia_ketab_bot", "BlackUploaderbot", # ربات ها رو اینجا اد کردم به لیست
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

# 🌐 دیتابیس‌های سراسری برنامه
SPONSOR_LINKS_ARCHIVE = set()
VISITED_BOT_PARAMS = set() 
GLOBAL_JOINED_CHANNELS = set() # 🎒 کوله‌پشتی کانال‌هایی که عضو شدیم برای لفت پایانی


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
    """ تلاش برای نفوذ به لینک‌های جوین‌چت و پرایوت """
    priv_match = re.search(r't\.me/(?:\+|joinchat/)([a-zA-Z0-9_-]+)', link)
    if priv_match:
        inv_hash = priv_match.group(1)
        try:
            res = await client(ImportChatInviteRequest(inv_hash))
            if hasattr(res, 'chats') and res.chats:
                ch_id = res.chats[0].id
                GLOBAL_JOINED_CHANNELS.add(ch_id)
                print(f"{depth_str}🥷 ورود موفق به کانال پرایوت اسپانسر!")
            await asyncio.sleep(2)
        except UserAlreadyParticipantError:
            pass
        except FloodWaitError as e:
            print(f"{depth_str}🛑 فلود ویت در جوین پرایوت: {e.seconds} ثانیه...")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"{depth_str}⚠️ خطا در ورود به لینک پرایوت: {e}")

async def handle_bot_interaction(client, bot_username, start_param, source_channel, source_post_id, depth=1):
    """ مدیریت هوشمند و بدون بازگشت ربات واسطه """
    global SPONSOR_LINKS_ARCHIVE, VISITED_BOT_PARAMS, GLOBAL_JOINED_CHANNELS
    
    unique_id = f"{bot_username}_{start_param}"
    if unique_id in VISITED_BOT_PARAMS:
        print(f"{'  '*depth}♻️ اسکیپ: قبلاً به @{bot_username} با این شناسه سر زدیم.")
        return
        
    VISITED_BOT_PARAMS.add(unique_id)
    print(f"\n{'  '*depth}🤖 ارتباط با ربات: @{bot_username} (شناسه: {start_param})")
    
    try:
        # ۱. ارسال استارت به ربات
        try:
            sent_msg = await client.send_message(bot_username, f"/start {start_param}")
        except FloodWaitError as e:
            if e.seconds < 45:
                await asyncio.sleep(e.seconds + 2)
                sent_msg = await client.send_message(bot_username, f"/start {start_param}")
            else:
                return

        await asyncio.sleep(4) 

        # دریافت پیام پاسخ ربات
        bot_response = None
        async for m in client.iter_messages(bot_username, limit=3):
            if m.id != sent_msg.id:
                bot_response = m
                break

        if not bot_response:
            print(f"{'  '*depth}⚠️ ربات پاسخی نداد.")
            return

        text = bot_response.text or ""
        if any(w in text for w in ["شماره", "احراز هویت", "ارسال شماره", "phone", "مخاطب"]):
            print(f"{'  '*depth}🛑 تله شماره تلفن! اسکیپ شد.")
            return

        # ۲. پردازش دکمه‌ها و عضویت در کانال‌های اسپانسر
        verify_btn_text = None

        if bot_response.reply_markup and hasattr(bot_response.reply_markup, 'rows'):
            for row in bot_response.reply_markup.rows:
                for btn in row.buttons:
                    # بررسی لینک دکمه‌ها
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
                                    print(f"{'  '*depth}📢 عضو کانال اسپانسر شدیم: @{target_c}")
                                    await asyncio.sleep(2)
                        except UserAlreadyParticipantError:
                            pass
                        except Exception as e:
                            print(f"{'  '*depth}⚠️ خطای عضویت: {e}")

                    # پیدا کردن دکمه بررسی عضویت
                    btn_text = getattr(btn, 'text', '')
                    if any(kw in btn_text for kw in ["بررسی", "تایید", "عضو شدم", "دریافت"]):
                        verify_btn_text = btn_text

            # ۳. کلیک تضمینی روی دکمه «بررسی عضویت» با تطبیق متن
            if verify_btn_text:
                print(f"{'  '*depth}🔘 همه کانال‌ها عضو شدند؛ فشردن «{verify_btn_text}»...")
                await asyncio.sleep(2)
                try:
                    await asyncio.wait_for(bot_response.click(text=verify_btn_text), timeout=10.0)
                except Exception as click_err:
                    print(f"{'  '*depth}⚠️ تلاش مجدد برای کلیک با ایندکس...")
                    try:
                        await bot_response.click(len(bot_response.reply_markup.rows) - 1, 0)
                    except Exception as e:
                        print(f"{'  '*depth}❌ خطا در کلیک: {e}")

                # صبر ضروری تا فرح استعلام بگیره و فایل رو رو کنه!
                print(f"{'  '*depth}⏳ در حال انتظار برای ارسال فایل (۶ ثانیه)...")
                await asyncio.sleep(6)

        # ۴. صید فایل تحویل داده شده
        file_found = False
        async for bot_msg in client.iter_messages(bot_username, limit=3):
            if bot_msg.document and bot_msg.document.mime_type == 'application/pdf':
                b_file = "فایل_دریافتی.pdf"
                for attr in bot_msg.document.attributes:
                    if isinstance(attr, DocumentAttributeFilename) and attr.file_name:
                        b_file = attr.file_name
                
                print(f"{'  '*depth}🎉 هورااا! فایل با موفقیت شکار شد: {b_file}")
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
                        send_to_telegram("لینک مستقیم فایل", link, tags, f"ربات @{bot_username}")
                        file_found = True
                        break
                 if file_found:
                     break

        if not file_found:
            print(f"{'  '*depth}⚠️ فایل توسط ربات ارسال نشد.")

    except Exception as e:
        print(f"{'  '*depth}⚠️ خطای پردازش ربات: {e}")


async def cleanup_all_joined_channels(client):
    """ خروج مؤدبانه و یکجا از تمام کانال‌ها در آخر کار """
    global GLOBAL_JOINED_CHANNELS
    if not GLOBAL_JOINED_CHANNELS:
        print("🧹 هیچ کانال اسپانسری در لیست خروج وجود ندارد.")
        return
        
    print(f"\n🚪 شروع پاکسازی ردپاها: در حال خروج از {len(GLOBAL_JOINED_CHANNELS)} چت/کانال...")
    for ch in list(GLOBAL_JOINED_CHANNELS):
        try:
            await client(LeaveChannelRequest(ch))
            print(f"👋 خروج موفق از: {ch}")
            await asyncio.sleep(2)
        except FloodWaitError as e:
            print(f"🛑 فلود ویت در زمان خروج! {e.seconds} ثانیه...")
            await asyncio.sleep(e.seconds)
        except Exception:
            pass
            
    GLOBAL_JOINED_CHANNELS.clear()
    print("✨ اکانت کاملاً پاکسازی شد!")


async def main():
    print("🦖 توربین با مغز ضد-لوپ و شکارچی فرح فعال شد!")
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
            print(f"🚜 در حال شخم زدن کانال: @{ch_clean}")
            print(f"======================================")

            try:
                # لیمیت ۳۰۰ پست برای جلوگیری از اسپم شدید و قفل شدن
                async for msg in client.iter_messages(ch_clean, limit=300):
                    if msg.date < week_ago:
                        break

                    # ۱. بررسی فایل مستقیم
                    if msg.document and msg.document.mime_type == 'application/pdf':
                        file_name = "فایل.pdf"
                        for attr in msg.document.attributes:
                            if isinstance(attr, DocumentAttributeFilename) and attr.file_name:
                                file_name = attr.file_name
                        
                        tags = extract_tags(file_name + " " + (msg.text or ""))
                        post_url = f"https://t.me/{ch_clean}/{msg.id}"
                        send_to_telegram(file_name, post_url, tags, ch_clean)
                        continue

                    # ۲. بررسی لینک‌های استارت ربات واسطه
                    search_text = msg.text or ""
                    if msg.reply_markup and hasattr(msg.reply_markup, 'rows'):
                        for row in msg.reply_markup.rows:
                            for btn in row.buttons:
                                if hasattr(btn, 'url') and btn.url:
                                    search_text += f" {btn.url} "

                    bot_links = re.findall(r't\.me/([a-zA-Z0-9_]+)\?start=([a-zA-Z0-9_-]+)', search_text)
                    for b_user, s_param in bot_links:
                        await handle_bot_interaction(client, b_user, s_param, ch_clean, msg.id, depth=1)
                        # استراحت بین استارت‌ها مثل رفتار کاربر انسانی
                        await asyncio.sleep(4)

            except Exception as e:
                print(f"❌ خطا در کانال @{ch_clean}: {e}")

        # ذخیره آرشیو لینک‌ها در پایان
        if SPONSOR_LINKS_ARCHIVE:
            os.makedirs("channels", exist_ok=True)
            today_str = datetime.now().strftime("%Y-%m-%d")
            file_path = os.path.join("channels", f"sponsor_links_{today_str}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                for link in sorted(SPONSOR_LINKS_ARCHIVE):
                    f.write(link + "\n")
            print(f"\n📁 {len(SPONSOR_LINKS_ARCHIVE)} لینک اسپانسر در {file_path} آرشیو شد.")

        print("\n🏁 تمام کانال‌ها اسکن شدند.")

    finally:
        # پاکسازی کانال‌ها بدون اینکه وسط کار مزاحم تحویل فایل بشه
        await cleanup_all_joined_channels(client)


if __name__ == "__main__":
    asyncio.run(main())
