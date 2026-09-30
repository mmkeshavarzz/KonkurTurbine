"""
=============================================================================
*  Project: Konkur PDF Hunter 🎓 (INCEPTION & FORCE-JOIN EDITION 🥷)
*  Author: mm.keshavarzz | Supercharged by Senior AI 👨‍💻
*  Features:
*    - Auto-Join Sponsor Channels & Private Groups (لینک‌های t.me/+ و joinchat) 📢
*    - Sponsor Scanner (شخم زدن کانال‌های اسپانسر برای فایل) 🚜
*    - Inception Bot-in-Bot (ورود به رباتِ داخل کانالِ اسپانسر تا عمق مشخص) 🌀
*    - Auto-Save Sponsor Links in /channels/YYYY-MM-DD.txt 📁
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
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors import UserAlreadyParticipantError

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

# 🌐 دیتابیس موقت برای ذخیره لینک‌های اسپانسر پیدا شده
SPONSOR_LINKS_ARCHIVE = set()

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

async def scan_sponsor_channel(client, sponsor_entity, source_channel_name, current_depth):
    """ جستجو داخل کانال/گروه اسپانسر (شخم زدن خواب لایه دوم) """
    print(f"   🔍 در حال اسکن اسپانسر: {sponsor_entity} (عمق: {current_depth})")
    try:
        # فقط 20 پیام آخر اسپانسر رو می‌خونیم که تلگرام بلاک نکنه
        async for msg in client.iter_messages(sponsor_entity, limit=20):
            # شکار فایل مستقیم تو کانال اسپانسر
            if msg.document and msg.document.mime_type == 'application/pdf':
                file_name = "فایل_اسپانسر.pdf"
                for attr in msg.document.attributes:
                    if isinstance(attr, DocumentAttributeFilename) and attr.file_name:
                        file_name = attr.file_name
                
                print(f"   🎯 فایل تو خود اسپانسر شکار شد! {file_name}")
                if TARGET_CHANNEL:
                    await client.forward_messages(TARGET_CHANNEL, msg)
                
                tags = extract_tags(file_name + " " + (msg.text or ""))
                post_url = f"https://t.me/c/{msg.chat_id}/{msg.id}" if hasattr(msg, 'chat_id') else ""
                send_to_telegram(file_name, post_url, tags, f"اسپانسرِ {source_channel_name}")
                continue

            # اگر عمق هنوز جا داره (عمق 1)، ربات‌های داخل اسپانسر رو هم می‌زنیم!
            if current_depth < 2:
                search_text = msg.text or ""
                if msg.reply_markup and hasattr(msg.reply_markup, 'rows'):
                    for row in msg.reply_markup.rows:
                        for btn in row.buttons:
                            if hasattr(btn, 'url') and btn.url:
                                search_text += f" {btn.url} "

                bot_links = re.findall(r't\.me/([a-zA-Z0-9_]+)\?start=([a-zA-Z0-9_-]+)', search_text)
                for b_user, s_param in bot_links:
                    print(f"   🌀 ورود به ربات تو در تو! پیدا شده در اسپانسر...")
                    await handle_bot_interaction(client, b_user, s_param, f"اسپانسرِ {source_channel_name}", msg.id, current_depth + 1)
                    await asyncio.sleep(2)
    except Exception as e:
        print(f"   ⚠️ خطا در اسکن اسپانسر {sponsor_entity}: {e}")


async def handle_bot_interaction(client, bot_username, start_param, source_channel, source_post_id, depth=1):
    """ مدیریت هوشمند ربات‌های واسطه و دور زدن جوین اجباری + ذخیره لینک‌ها """
    global SPONSOR_LINKS_ARCHIVE
    print(f"{'  '*depth}🤖 درگیری با ربات واسطه: @{bot_username} (عمق: {depth})")
    joined_entities = []
    
    try:
        await client.send_message(bot_username, f"/start {start_param}")
        await asyncio.sleep(3)

        bot_response = None
        async for m in client.iter_messages(bot_username, limit=1):
            bot_response = m
            break

        if not bot_response:
            return

        text = bot_response.text or ""
        
        # ⚠️ سپر امنیتی ۱: فرار از تله شماره موبایل
        if any(w in text for w in ["شماره", "احراز هویت", "ارسال شماره", "phone", "مخاطب"]):
            print(f"{'  '*depth}🛑 هشدار! ربات @{bot_username} تله شماره تلفن گذاشته. اسکیپ شد.")
            return

        # 📢 دور زدن قفل جوین اجباری (عمومی + خصوصی/گروه)
        if bot_response.reply_markup and hasattr(bot_response.reply_markup, 'rows'):
            verify_button = None
            
            for row in bot_response.reply_markup.rows:
                for btn in row.buttons:
                    if hasattr(btn, 'url') and btn.url:
                        # اضافه کردن لینک به دیتابیس آرشیو
                        SPONSOR_LINKS_ARCHIVE.add(btn.url)
                        
                        priv_match = re.search(r't\.me/(?:\+|joinchat/)([a-zA-Z0-9_-]+)', btn.url)
                        pub_match = re.search(r't\.me/([a-zA-Z0-9_]+)$', btn.url)

                        target_entity = None

                        # اگه لینک گروه پرایوت مثل همون "گپ فاک کلاس" بود:
                        if priv_match:
                            inv_hash = priv_match.group(1)
                            print(f"{'  '*depth}🕵️‍♂️ لینک خصوصی پیدا شد! ورود شبانه به هش: {inv_hash}")
                            try:
                                updates = await client(ImportChatInviteRequest(inv_hash))
                                if hasattr(updates, 'chats') and updates.chats:
                                    target_entity = updates.chats[0].id
                                    joined_entities.append(target_entity)
                                await asyncio.sleep(2)
                            except UserAlreadyParticipantError:
                                print(f"{'  '*depth}✅ از قبل تو این گپ پرایوت بودیم.")
                            except Exception as e:
                                print(f"{'  '*depth}⚠️ نتونست وارد گروه پرایوت بشه: {e}")

                        # اگه کانال عمومی بود:
                        elif pub_match:
                            target_c = pub_match.group(1)
                            if not target_c.lower().endswith('bot'):
                                print(f"{'  '*depth}➕ عضویت موقت در کانال عمومی: @{target_c}")
                                try:
                                    await client(JoinChannelRequest(target_c))
                                    target_entity = target_c
                                    joined_entities.append(target_entity)
                                    await asyncio.sleep(2)
                                except UserAlreadyParticipantError:
                                    pass
                                except Exception as e:
                                    print(f"{'  '*depth}⚠️ خطا تو عضویت @{target_c}: {e}")
                        
                        # 🚜 اگر با موفقیت جوین شدیم، حالا وقت شخم زدن اسپانسره!
                        if target_entity:
                            await scan_sponsor_channel(client, target_entity, source_channel, depth)

                    btn_text = getattr(btn, 'text', '')
                    if any(kw in btn_text for kw in ["بررسی", "تایید", "عضو شدم", "دریافت"]):
                        verify_button = btn

            if verify_button and hasattr(verify_button, 'data'):
                print(f"{'  '*depth}🔘 فشردن دکمه تایید عضویت...")
                await bot_response.click(data=verify_button.data)
                await asyncio.sleep(4)

        async for bot_msg in client.iter_messages(bot_username, limit=2):
            if bot_msg.document and bot_msg.document.mime_type == 'application/pdf':
                b_file = "فایل_مخفی.pdf"
                for attr in bot_msg.document.attributes:
                    if isinstance(attr, DocumentAttributeFilename) and attr.file_name:
                        b_file = attr.file_name
                
                print(f"{'  '*depth}🎯 پاداش! فایل مخفی گرفته شد: {b_file}")
                if TARGET_CHANNEL:
                    await client.forward_messages(TARGET_CHANNEL, bot_msg)
                
                post_url = f"https://t.me/{source_channel}/{source_post_id}"
                tags = extract_tags(b_file + " " + (bot_msg.text or ""))
                send_to_telegram(b_file, post_url, tags, f"{source_channel} (از چنگ @{bot_username})")
                break

    except Exception as e:
        print(f"{'  '*depth}⚠️ خطای ربات واسطه: {e}")
    finally:
        # 🧹 پاکسازی: لفت دادن نامحسوس
        for c in joined_entities:
            try:
                print(f"{'  '*depth}➖ خروج خودکار از اسپانسر: {c}")
                await client(LeaveChannelRequest(c))
                await asyncio.sleep(1)
            except:
                pass

async def main():
    print("🦖 موتور Inception توربین با قابلیت رخنه به گپ‌های خصوصی فعال شد!")
    if not SESSION_STRING:
        print("❌ سشن استرینگ وجود ندارد!")
        return

    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.start()
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)

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
                    # شروع چرخه با عمق 1
                    await handle_bot_interaction(client, b_user, s_param, ch_clean, msg.id, depth=1)
                    await asyncio.sleep(2)

        except Exception as e:
            print(f"❌ خطا در کانال @{ch_clean}: {e}")

    # 💾 ذخیره سازی لینک‌های اسپانسر در پوشه channels
    if SPONSOR_LINKS_ARCHIVE:
        os.makedirs("channels", exist_ok=True)
        today_str = datetime.now().strftime("%Y-%m-%d")
        file_path = os.path.join("channels", f"sponsor_links_{today_str}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            for link in sorted(SPONSOR_LINKS_ARCHIVE):
                f.write(link + "\n")
        print(f"\n📁 موفقیت: {len(SPONSOR_LINKS_ARCHIVE)} لینک اسپانسر در فایل {file_path} آرشیو شد تا بعداً بررسیشون کنی.")

    print("\n🏁 اسکن به اتمام رسید.")

if __name__ == "__main__":
    asyncio.run(main())

    print("\n🏁 اسکن به اتمام رسید.")

if __name__ == "__main__":
    asyncio.run(main())
