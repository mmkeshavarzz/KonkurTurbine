"""
=============================================================================
*  Project: Konkur PDF Hunter 🎓 (INCEPTION & FORCE-JOIN EDITION 🥷)
*  Author: mm.keshavarzz | Supercharged by Senior AI 👨‍💻
*  Features:
*    - 🎒 Global Delayed Cleanup (لفت دادن یکجا در انتهای کار برای دور زدن هوش ربات)
*    - 🛡️ Protector Shield Breaker (عبور از کانال‌های واسطه و نفوذ به لینک‌های مخفی داخلی)
*    - Auto-Join Sponsor Channels & Private Groups (لینک‌های t.me/+ و joinchat) 📢
*    - Sponsor Scanner (شخم زدن کانال‌های اسپانسر برای فایل) 🚜
*    - Inception Bot-in-Bot (ورود به رباتِ داخل کانالِ اسپانسر تا عمق مشخص) 🌀
*    - Anti-PhoneTrap Shield (فرار از تله ارسال شماره تلفن) 🛑
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

# 🌐 دیتابیس‌های سراسری برنامه
SPONSOR_LINKS_ARCHIVE = set()
VISITED_BOT_PARAMS = set() 
GLOBAL_JOINED_CHANNELS = set() # 🎒 کوله‌پشتی کانال‌هایی که عضو شدیم برای لفتِ پایانی!


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
                print(f"{depth_str}🥷 با موفقیت به کانال مخفی نفوذ کردیم!")
            await asyncio.sleep(2)
        except UserAlreadyParticipantError:
            pass # از قبل عضو بودیم، فدای سرمون!
        except FloodWaitError as e:
            print(f"{depth_str}🛑 فلود ویت در جوین پرایوت! {e.seconds} ثانیه...")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"{depth_str}⚠️ خطا در ورود به لینک مخفی: {e}")

async def scan_sponsor_channel(client, sponsor_entity, source_channel_name, current_depth):
    """ جستجو داخل کانال اسپانسر و شکستن طلسم کانال‌های واسطه (Protector Channels) """
    depth_str = '  ' * current_depth
    print(f"{depth_str}🔍 در حال اسکن اسپانسر: {sponsor_entity} (عمق: {current_depth})")
    
    try:
        # فقط 10 پیام آخر اسپانسر رو می‌خونیم
        async for msg in client.iter_messages(sponsor_entity, limit=10):
            # 🎯 ۱. شکار فایل مستقیم
            if msg.document and msg.document.mime_type == 'application/pdf':
                file_name = "فایل_اسپانسر.pdf"
                for attr in msg.document.attributes:
                    if isinstance(attr, DocumentAttributeFilename) and attr.file_name:
                        file_name = attr.file_name
                
                print(f"{depth_str}🎯 فایل تو خود اسپانسر شکار شد! {file_name}")
                if TARGET_CHANNEL:
                    await client.forward_messages(TARGET_CHANNEL, msg)
                
                tags = extract_tags(file_name + " " + (msg.text or ""))
                post_url = f"https://t.me/c/{msg.chat_id}/{msg.id}" if hasattr(msg, 'chat_id') else ""
                send_to_telegram(file_name, post_url, tags, f"اسپانسرِ {source_channel_name}")
                continue

            # 🛡️ ۲. شکستن طلسم کانال محافظ (پیدا کردن لینک‌های جوین‌چت در کانال‌های عمومی)
            text = msg.text or ""
            priv_links = re.findall(r'(https?://t\.me/(?:\+|joinchat/)[a-zA-Z0-9_-]+)', text)
            for pl in priv_links:
                print(f"{depth_str}🛡️ لینک کانال اصلی (پشت واسطه) کشف شد! در حال نفوذ...")
                SPONSOR_LINKS_ARCHIVE.add(pl)
                await try_join_private_link(client, pl, depth_str + '  ')

            # 🌀 ۳. پیدا کردن ربات‌های تو در تو
            if current_depth < 2:
                search_text = text
                if msg.reply_markup and hasattr(msg.reply_markup, 'rows'):
                    for row in msg.reply_markup.rows:
                        for btn in row.buttons:
                            if hasattr(btn, 'url') and btn.url:
                                search_text += f" {btn.url} "

                bot_links = re.findall(r't\.me/([a-zA-Z0-9_]+)\?start=([a-zA-Z0-9_-]+)', search_text)
                for b_user, s_param in bot_links:
                    print(f"{depth_str}🌀 ورود به ربات تو در تو! پیدا شده در اسپانسر...")
                    await handle_bot_interaction(client, b_user, s_param, f"اسپانسرِ {source_channel_name}", msg.id, current_depth + 1)
                    await asyncio.sleep(2)
    except Exception as e:
        print(f"{depth_str}⚠️ خطا در اسکن اسپانسر {sponsor_entity}: {e}")

async def handle_bot_interaction(client, bot_username, start_param, source_channel, source_post_id, depth=1):
    """ مدیریت ربات‌های واسطه، جوین اجباری و کلیک با حوصله! """
    global SPONSOR_LINKS_ARCHIVE, VISITED_BOT_PARAMS, GLOBAL_JOINED_CHANNELS
    
    unique_id = f"{bot_username}_{start_param}"
    if unique_id in VISITED_BOT_PARAMS:
        print(f"{'  '*depth}♻️ اسکیپ شد: این ربات (@{bot_username}) تکراری است.")
        return
        
    VISITED_BOT_PARAMS.add(unique_id)
    print(f"{'  '*depth}🤖 درگیری با ربات واسطه: @{bot_username}")
    
    try:
        try:
            sent_msg = await client.send_message(bot_username, f"/start {start_param}")
        except FloodWaitError as e:
            if e.seconds < 60:
                await asyncio.sleep(e.seconds + 2)
                sent_msg = await client.send_message(bot_username, f"/start {start_param}")
            else:
                return

        await asyncio.sleep(4) 

        bot_response = None
        async for m in client.iter_messages(bot_username, limit=3):
            if m.id != sent_msg.id:
                bot_response = m
                break

        if not bot_response:
            return

        text = bot_response.text or ""
        if any(w in text for w in ["شماره", "احراز هویت", "ارسال شماره", "phone", "مخاطب"]):
            print(f"{'  '*depth}🛑 تله شماره موبایل! اسکیپ شد.")
            return

        # پیدا کردن لینک‌های دانلود مستقیم توی متن پیام
        text_links = re.findall(r'(https?://t\.me/[^\s]+)', text)
        for link in text_links:
            if TARGET_CHANNEL and not "start=" in link:
                tags = extract_tags(text)
                send_to_telegram("لینک کشف شده از متن ربات", link, tags, f"{source_channel} (از چنگ @{bot_username})")

        # پردازش دکمه‌ها (عضویت‌ها)
        if bot_response.reply_markup and hasattr(bot_response.reply_markup, 'rows'):
            verify_button_coords = None
            
            for row_idx, row in enumerate(bot_response.reply_markup.rows):
                for col_idx, btn in enumerate(row.buttons):
                    if hasattr(btn, 'url') and btn.url:
                        SPONSOR_LINKS_ARCHIVE.add(btn.url)
                        
                        priv_match = re.search(r't\.me/(?:\+|joinchat/)([a-zA-Z0-9_-]+)', btn.url)
                        pub_match = re.search(r't\.me/([a-zA-Z0-9_]+)$', btn.url)
                        target_entity = None

                        try:
                            if priv_match:
                                await try_join_private_link(client, btn.url, '  '*depth)
                            elif pub_match:
                                target_c = pub_match.group(1)
                                if not target_c.lower().endswith('bot'):
                                    await client(JoinChannelRequest(target_c))
                                    target_entity = target_c
                                    GLOBAL_JOINED_CHANNELS.add(target_entity)
                                    await asyncio.sleep(2)
                        except UserAlreadyParticipantError:
                            pass
                        except Exception as e:
                            print(f"{'  '*depth}⚠️ خطا در جوین: {e}")

                        # اگه کانال عمومی بود، سریع اسکنش می‌کنیم تا لینک‌های پرایوت مخفی (واسطه‌ها) رو پیدا کنیم!
                        if target_entity:
                            await scan_sponsor_channel(client, target_entity, source_channel, depth)

                    btn_text = getattr(btn, 'text', '')
                    if any(kw in btn_text for kw in ["بررسی", "تایید", "عضو شدم", "دریافت"]):
                        verify_button_coords = (row_idx, col_idx)

            # دکمه بررسی عضویت رو با Timeout ایمن فشار میدیم
            if verify_button_coords is not None:
                r_idx, c_idx = verify_button_coords
                print(f"{'  '*depth}🔘 در حال فشردن دکمه «بررسی عضویت»...")
                try:
                    await asyncio.wait_for(
                        bot_response.click(r_idx, c_idx),
                        timeout=12.0
                    )
                except asyncio.TimeoutError:
                    print(f"{'  '*depth}⏳ تایم‌اوت در کلیک (احتمالاً ربات در حال پردازش است).")
                except Exception as click_err:
                    print(f"{'  '*depth}⚠️ مشکل در کلیک دکمه: {click_err}")
                
                await asyncio.sleep(6) # صبر برای ارسال فایل

        # بررسی پیام‌های جدید برای صید فایل
        async for bot_msg in client.iter_messages(bot_username, limit=3):
            if bot_msg.document and bot_msg.document.mime_type == 'application/pdf':
                b_file = "فایل_مخفی.pdf"
                for attr in bot_msg.document.attributes:
                    if isinstance(attr, DocumentAttributeFilename) and attr.file_name:
                        b_file = attr.file_name
                
                print(f"{'  '*depth}🎯 شکار شد! فایل تحویل گرفته شد: {b_file}")
                if TARGET_CHANNEL:
                    await client.forward_messages(TARGET_CHANNEL, bot_msg)
                
                post_url = f"https://t.me/{source_channel}/{source_post_id}"
                tags = extract_tags(b_file + " " + (bot_msg.text or ""))
                send_to_telegram(b_file, post_url, tags, f"{source_channel} (از چنگ @{bot_username})")
                break
            
            elif bot_msg.text and bot_msg.id != sent_msg.id:
                 text_links = re.findall(r'(https?://t\.me/[^\s]+)', bot_msg.text)
                 for link in text_links:
                    if not "start=" in link:
                        tags = extract_tags(bot_msg.text)
                        send_to_telegram("لینک فایل (غیر مستقیم)", link, tags, f"ربات @{bot_username}")

    except Exception as e:
        print(f"{'  '*depth}⚠️ خطای پردازش ربات: {e}")
    # 🔴 اینجا دیگه لفت نمی‌دیم! لفت دادن رفت برای آخرِ آخر برنامه!


async def cleanup_all_joined_channels(client):
    """ 🧹 پاکسازی بزرگ در انتهای برنامه """
    global GLOBAL_JOINED_CHANNELS
    if not GLOBAL_JOINED_CHANNELS:
        return
        
    print(f"\n🚪 عملیات پاکسازی: در حال خروج یکجا از {len(GLOBAL_JOINED_CHANNELS)} چت/کانال...")
    for ch in list(GLOBAL_JOINED_CHANNELS):
        try:
            await client(LeaveChannelRequest(ch))
            print(f"👋 خروج موفق از: {ch}")
            await asyncio.sleep(2)
        except FloodWaitError as e:
            print(f"🛑 فلود ویت در زمان خروج! {e.seconds} ثانیه...")
            await asyncio.sleep(e.seconds)
        except Exception:
            pass # باگ‌های جزئی خروج رو ایگنور می‌کنیم
            
    GLOBAL_JOINED_CHANNELS.clear()
    print("✨ تمام ردپاهای ربات پاک شد!")


async def main():
    print("🦖 موتور Inception توربین با قابلیت رخنه به گپ‌های خصوصی فعال شد!")
    if not SESSION_STRING:
        print("❌ سشن استرینگ وجود ندارد!")
        return

    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.start()
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)

    try:
        for ch in CHANNELS:
            ch_clean = ch.replace('@', '')
            print(f"\n🚜 شخم زدن منبع اصلی: @{ch_clean}")

            try:
                async for msg in client.iter_messages(ch_clean, limit=1000):
                    if msg.date < week_ago:
                        break

                    if msg.document and msg.document.mime_type == 'application/pdf':
                        file_name = "فایل.pdf"
                        for attr in msg.document.attributes:
                            if isinstance(attr, DocumentAttributeFilename) and attr.file_name:
                                file_name = attr.file_name
                        
                        tags = extract_tags(file_name + " " + (msg.text or ""))
                        post_url = f"https://t.me/{ch_clean}/{msg.id}"
                        send_to_telegram(file_name, post_url, tags, ch_clean)
                        continue

                    search_text = msg.text or ""
                    if msg.reply_markup and hasattr(msg.reply_markup, 'rows'):
                        for row in msg.reply_markup.rows:
                            for btn in row.buttons:
                                if hasattr(btn, 'url') and btn.url:
                                    search_text += f" {btn.url} "

                    bot_links = re.findall(r't\.me/([a-zA-Z0-9_]+)\?start=([a-zA-Z0-9_-]+)', search_text)
                    for b_user, s_param in bot_links:
                        await handle_bot_interaction(client, b_user, s_param, ch_clean, msg.id, depth=1)
                        await asyncio.sleep(2)

            except Exception as e:
                print(f"❌ خطا در کانال @{ch_clean}: {e}")

        # 💾 آرشیو لینک‌ها
        if SPONSOR_LINKS_ARCHIVE:
            os.makedirs("channels", exist_ok=True)
            today_str = datetime.now().strftime("%Y-%m-%d")
            file_path = os.path.join("channels", f"sponsor_links_{today_str}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                for link in sorted(SPONSOR_LINKS_ARCHIVE):
                    f.write(link + "\n")
            print(f"\n📁 موفقیت: {len(SPONSOR_LINKS_ARCHIVE)} لینک اسپانسر ذخیره شد.")

        print("\n🏁 اسکن به اتمام رسید.")

    finally:
        # 🧼 اینجا هر اتفاقی بیفته، حتی اگر وسط کار ارور بده، میاد و لفت میده!
        await cleanup_all_joined_channels(client)


if __name__ == "__main__":
    asyncio.run(main())
