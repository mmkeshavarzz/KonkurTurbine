"""
=============================================================================
*  Project: Konkur PDF Hunter 🎓 (FRIDAY EXAM EDITION - FULL 7 DAYS)
*  Features:
*    - 📅 Full 7-Day Sweep: پوشش کامل آزمون‌های جمعه و آرشیو یک هفته گذشته
*    - 🧠 Cloud Memory: بررسی تاریخچه استارت‌ها در تلگرام تا ۲۰۰ پیام گذشته
*    - 🛑 Anti-Spam Guard: ترمز اضطراری هوشمند برای حفظ سلامت اکانت
*    - 🎒 End-of-Run Cleanup: خروج دسته‌جمعی از کانال‌ها در پایان ماموریت
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
    "fiziikkonkoor", "shimiikonkoor", "riaziikonkor", 
    "konkurbartar3", "Konkor_Elite", "MafiaKetab", 
    "KoroshKabir_bot", "Senatorjani_bot", "HYPEJOZVE_BOT", "mafia_ketab_bot", "BlackUploaderbot"
]

TAGS_DICTIONARY = {
    "رشته": {"🧬 تجربی": ["تجربی", "تجر", "biology"], "📐 ریاضی": ["ریاضی", "ریاض"], "⚖️ انسانی": ["انسانی", "فلسفه", "ادبیات_تخصصی"]},
    "آزمون": {"سراسری": ["سراسری", "کنکور"], "قلم‌چی": ["قلم", "قلمچی", "کانون"], "ماز": ["ماز"], "گاج": ["گاج"], "گزینه دو": ["گزینه", "گزینه۲"], "خیلی سبز": ["خیلی_سبز"]},
    "درس": {"زیست‌شناسی": ["زیست", "گیاهی", "جانوری"], "شیمی": ["شیمی"], "فیزیک": ["فیزیک"], "ریاضیات": ["حسابان", "هندسه", "گسسته", "آمار", "ریاضی"]}
}

API_ID = int(os.environ.get("TELEGRAM_API_ID", 2040))
API_HASH = os.environ.get("TELEGRAM_API_HASH", "")
SESSION_STRING = os.environ.get("TELEGRAM_SESSION", "")
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TARGET_CHANNEL = os.environ.get("TELEGRAM_CHANNEL", "")

# 🌐 متغیرهای گلوبال و حافظه کلود
SPONSOR_LINKS_ARCHIVE = set()
VISITED_BOT_PARAMS = set()
GLOBAL_JOINED_CHANNELS = set()
LOADED_BOT_HISTORIES = set()
CONSECUTIVE_BOT_FAILS = 0


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
    msg = (f"🧨 <b>شکار جدید توربین!</b>\n━━━━━━━━━━━━━━━━━━━\n"
           f"📄 <b>عنوان فایل:</b>\n<blockquote>{file_title}</blockquote>\n"
           f"{f'{details}' if details else ''}━━━━━━━━━━━━━━━━━━━\n"
           f"📡 <b>منبع:</b> @{source_channel}\n"
           f"📥 <a href='{post_url}'>[ ☁️ مشاهده/دانلود فایل ]</a>")

    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      json={"chat_id": TARGET_CHANNEL, "text": msg, "parse_mode": "HTML", "disable_web_page_preview": True}, timeout=10)
    except Exception as e:
        print(f"❌ خطا در ارسال بنر: {e}")

async def try_join_private_link(client, link, depth_str=""):
    priv_match = re.search(r't\.me/(?:\+|joinchat/)([a-zA-Z0-9_-]+)', link)
    if priv_match:
        inv_hash = priv_match.group(1)
        try:
            res = await client(ImportChatInviteRequest(inv_hash))
            if hasattr(res, 'chats') and res.chats:
                GLOBAL_JOINED_CHANNELS.add(res.chats[0].id)
            await asyncio.sleep(2)
        except UserAlreadyParticipantError:
            pass
        except FloodWaitError as e:
            print(f"{depth_str}🛑 فلود ویت در جوین پرایوت: {e.seconds} ثانیه...")
            await asyncio.sleep(e.seconds)
        except Exception:
            pass

async def load_bot_history(client, bot_username):
    """ بازیابی تا ۲۰۰ استارت اخیر از سرور تلگرام برای جلوگیری از شلیک تکراری """
    if bot_username in LOADED_BOT_HISTORIES:
        return
    print(f"🔄 بازیابی حافظه چت با @{bot_username} از کلود تلگرام...")
    try:
        async for m in client.iter_messages(bot_username, limit=200, search='/start'):
            if m.text and m.text.startswith('/start '):
                parts = m.text.split(' ')
                if len(parts) > 1:
                    VISITED_BOT_PARAMS.add(f"{bot_username}_{parts[1]}")
    except Exception as e:
        print(f"⚠️ خطا در خواندن تاریخچه: {e}")
    LOADED_BOT_HISTORIES.add(bot_username)


async def handle_bot_interaction(client, bot_username, start_param, source_channel, source_post_id, depth=1):
    global SPONSOR_LINKS_ARCHIVE, VISITED_BOT_PARAMS, GLOBAL_JOINED_CHANNELS, CONSECUTIVE_BOT_FAILS
    
    # اگر ربات کلاً از کار افتاده باشه و ۳ بار متوالی فایل نده، جهت حفظ امنیت متوقف میشه
    if CONSECUTIVE_BOT_FAILS >= 3:
        print(f"{'  '*depth}🚨 ترمز اضطراری: به دلیل خطای متوالی ربات واسطه، آیتم جاری اسکیپ شد.")
        return

    await load_bot_history(client, bot_username)

    unique_id = f"{bot_username}_{start_param}"
    if unique_id in VISITED_BOT_PARAMS:
        print(f"{'  '*depth}♻️ اسکیپ: فایل قبلاً دریافت شده (شناسه: {start_param})")
        return
        
    VISITED_BOT_PARAMS.add(unique_id)
    print(f"\n{'  '*depth}🤖 ارتباط با ربات: @{bot_username} (شناسه: {start_param})")
    
    try:
        sent_msg = await client.send_message(bot_username, f"/start {start_param}")
        await asyncio.sleep(4) 

        bot_response = None
        async for m in client.iter_messages(bot_username, limit=3):
            if m.id != sent_msg.id:
                bot_response = m
                break

        if not bot_response:
            return

        text = bot_response.text or ""
        if any(w in text for w in ["شماره", "احراز هویت", "ارسال شماره"]):
            print(f"{'  '*depth}🛑 تله شماره تلفن! اسکیپ شد.")
            return

        verify_btn_text = None
        if bot_response.reply_markup and hasattr(bot_response.reply_markup, 'rows'):
            for row in bot_response.reply_markup.rows:
                for btn in row.buttons:
                    if hasattr(btn, 'url') and btn.url:
                        SPONSOR_LINKS_ARCHIVE.add(btn.url)
                        try:
                            if "joinchat" in btn.url or "+" in btn.url:
                                await try_join_private_link(client, btn.url, '  '*depth)
                            else:
                                pub_match = re.search(r't\.me/([a-zA-Z0-9_]+)$', btn.url)
                                if pub_match and not pub_match.group(1).lower().endswith('bot'):
                                    target_c = pub_match.group(1)
                                    await client(JoinChannelRequest(target_c))
                                    GLOBAL_JOINED_CHANNELS.add(target_c)
                                    await asyncio.sleep(2)
                        except (UserAlreadyParticipantError, FloodWaitError):
                            pass
                        except Exception:
                            pass

                    btn_text = getattr(btn, 'text', '')
                    if any(kw in btn_text for kw in ["بررسی", "تایید", "عضو شدم", "دریافت"]):
                        verify_btn_text = btn_text

            if verify_btn_text:
                print(f"{'  '*depth}🔘 فشردن کلید تایید/بررسی عضویت...")
                await asyncio.sleep(2)
                try:
                    await bot_response.click(len(bot_response.reply_markup.rows) - 1, 0)
                except Exception:
                    try:
                        await bot_response.click(text=verify_btn_text)
                    except Exception:
                        pass
                await asyncio.sleep(6)

        # دریافت فایل ارسالی
        file_found = False
        async for bot_msg in client.iter_messages(bot_username, limit=3):
            if bot_msg.document and bot_msg.document.mime_type in ['application/pdf', 'application/x-rar-compressed', 'application/zip']:
                b_file = "فایل_دریافتی.pdf"
                for attr in bot_msg.document.attributes:
                    if isinstance(attr, DocumentAttributeFilename) and attr.file_name:
                        b_file = attr.file_name
                
                print(f"{'  '*depth}🎉 هورااا! فایل شکار شد: {b_file}")
                if TARGET_CHANNEL:
                    await client.forward_messages(TARGET_CHANNEL, bot_msg)
                
                post_url = f"https://t.me/{source_channel}/{source_post_id}"
                send_to_telegram(b_file, post_url, extract_tags(b_file + " " + (bot_msg.text or "")), f"{source_channel} (از چنگ @{bot_username})")
                file_found = True
                break

        if not file_found:
            print(f"{'  '*depth}⚠️ فایلی دریافت نشد.")
            CONSECUTIVE_BOT_FAILS += 1
        else:
            CONSECUTIVE_BOT_FAILS = 0

    except Exception as e:
        print(f"{'  '*depth}⚠️ خطای پردازش: {e}")


async def cleanup_all_joined_channels(client):
    if not GLOBAL_JOINED_CHANNELS:
        return
    print(f"\n🚪 پاکسازی نهایی: خروج از {len(GLOBAL_JOINED_CHANNELS)} کانال اسپانسر...")
    for ch in list(GLOBAL_JOINED_CHANNELS):
        try:
            await client(LeaveChannelRequest(ch))
            await asyncio.sleep(2)
        except Exception:
            pass
    GLOBAL_JOINED_CHANNELS.clear()


async def main():
    print("🦖 توربین نسخه ویژه جمعه کنکوری (۷ روز کامل) به پرواز درآمد!")
    if not SESSION_STRING:
        print("❌ سشن استرینگ تلگرام یافت نشد!")
        return

    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.start()
    
    # 🗓️ ۷ روز کامل به درخواست مستقیم شما برای فایل‌های روز جمعه
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)

    try:
        for ch in CHANNELS:
            ch_clean = ch.replace('@', '')
            print(f"\n🚜 اسکن عمیق کانال: @{ch_clean}")

            try:
                # سقف تا ۵۰۰ پست در هفته
                async for msg in client.iter_messages(ch_clean, limit=500):
                    if msg.date < week_ago:
                        break

                    # ۱. فایل PDF مستقیم
                    if msg.document and msg.document.mime_type == 'application/pdf':
                        file_name = "فایل.pdf"
                        for attr in msg.document.attributes:
                            if isinstance(attr, DocumentAttributeFilename) and attr.file_name:
                                file_name = attr.file_name
                        post_url = f"https://t.me/{ch_clean}/{msg.id}"
                        send_to_telegram(file_name, post_url, extract_tags(file_name + " " + (msg.text or "")), ch_clean)
                        continue

                    # ۲. بررسی لینک‌های ربات واسطه (مثل ملکه فرح و کوروش کبیر)
                    search_text = msg.text or ""
                    if msg.reply_markup and hasattr(msg.reply_markup, 'rows'):
                        for row in msg.reply_markup.rows:
                            for btn in row.buttons:
                                if hasattr(btn, 'url') and btn.url:
                                    search_text += f" {btn.url} "

                    bot_links = re.findall(r't\.me/([a-zA-Z0-9_]+)\?start=([a-zA-Z0-9_-]+)', search_text)
                    for b_user, s_param in bot_links:
                        await handle_bot_interaction(client, b_user, s_param, ch_clean, msg.id, depth=1)
                        await asyncio.sleep(4)

            except Exception as e:
                print(f"❌ خطا در کانال @{ch_clean}: {e}")

        # آرشیو لینک‌ها
        if SPONSOR_LINKS_ARCHIVE:
            os.makedirs("channels", exist_ok=True)
            with open(os.path.join("channels", "sponsor_links.txt"), "w", encoding="utf-8") as f:
                for link in sorted(SPONSOR_LINKS_ARCHIVE):
                    f.write(link + "\n")

    finally:
        await cleanup_all_joined_channels(client)


if __name__ == "__main__":
    asyncio.run(main())
