#The code was created and developed by (Saleh) from the "Open Source Tools" team. 
from setup import *
setup()
import re
import os
from uuid import *
import traceback
import json
import logging
from telegram import (
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    PicklePersistence,
    CallbackContext,
    CallbackQueryHandler,
    ContextTypes,
    InlineQueryHandler,
)
import html
from pytube import YouTube, Search
import json

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

DEVELOPER_CHAT_ID = 1234567890  #Input: int, value: Telegram channel/user.
video_max = 8  # Duration: minutes
audio_max = 60  # Duration: minutes






with open('users.json', 'r') as f:
  users = json.load(f)
with open('translations.json', 'r') as f:
  translations = json.load(f)

# تعريف دالة للتعامل مع أمر /lang
async def lang(update, context):
  # الحصول على معرف المستخدم ولغته الحالية
  user_id = update.message.from_user.id
  # استخدام لغة المستخدم الفعالة كلغة افتراضية إذا لم يكن للمستخدم لغة محددة بالملف
  user_lang = users.get(int(user_id), {"language": str(update.effective_user.language_code)})
  # إنشاء قائمة أزرار للغات المتاحة
  buttons = []
  # فرز اللغات حسب رمز اللغة من A إلى Z
  languages = sorted(translations.items(), key=lambda x: x, reverse=False)
  for lang_code, lang_name in languages:
      # تجاهل اللغة التي تساوي user_lang
      #if lang_code != user_lang["language"]:
          buttons.append([
              InlineKeyboardButton(lang_name["language"], callback_data=lang_code)
          ])
  # إنشاء كائن من نوع InlineKeyboardMarkup
  keyboard = InlineKeyboardMarkup(buttons)
  # تقسيم الأزرار إلى صفوف من 3 أزرار في كل صف
  await update.message.reply_text(
      translations[user_lang["language"]]["choose_lang"], reply_markup=keyboard
)

# تعريف دالة للتعامل مع النقر على الأزرار
async def button(update, context):
  # الحصول على معرف المستخدم والبيانات المرسلة من الزر
  user_id = update.callback_query.from_user.id
  data = update.callback_query.data
  # تحديث لغة المستخدم في ملف users.json إذا كانت مختلفة عن البيانات
  if users.get(str(user_id)) != data:
      users[int(user_id)] = {"language": data}
      with open('users.json', 'w') as f:
          json.dump(users, f, indent=4)
  # إرسال رسالة تأكيد للمستخدم
  try:
      await update.callback_query.edit_message_text(
          translations[data]["lang_changed"]
      )
  except Exception as e:
      await update.callback_query.edit_message_text(
          f"❌️ | `{e}`"
      )



markup = InlineKeyboardMarkup([[
  InlineKeyboardButton(text="📚", url="https://t.me/yellow_tube"),
  InlineKeyboardButton(text="💵", url="https://paypal.com/paypalme/lineset"),
]]) #Change the links or button names here. If you want to.




def check_user_id(user_id, dicts):
  for d in dicts:
      value = d.get(user_id)
      if value is not None:
          return True
  return False

async def start(update, context):
  try:
      user_id = update.message.from_user.id
      # تحميل ملفات json للمستخدمين والترجمات
      with open('users.json', 'r') as f:
          users = json.load(f)
      with open('translations.json', 'r') as f:
          translations = json.load(f)
      # الحصول على لغة المستخدم من ملف users.json أو من update.effective_user.language_code كبديل
      user_language = users.get(str(user_id), update.effective_user.language_code) # استخدم القيمة الافتراضية للمفتاح إذا لم يتم العثور عليه
      # التحقق من إذا كان معرف المستخدم موجود في أي قاموس أو لا
      if not check_user_id(str(user_id), [users, translations]): # استخدم str(user_id) كمعرف لتوحيد نوع البيانات
          # إضافة معرف المستخدم ولغته إلى ملف users.json
          users[str(user_id)] = {"language": user_language} # استخدم str(user_id) كمفتاح لتوحيد نوع البيانات
          with open('users.json', 'w') as f:
              json.dump(users, f, indent=4)
      # الحصول على الرد الجاهز من بيانات الترجمات
      response = translations[user_language["language"]]["start_message"] # استخدم user_language["language"] كمفتاح بدلاً من user_language
      # استخدم user_language كمفتاح بدلاً من user_language["language"]
      # تنسيق الرد بمعرف البوت
      response = response.format(bot_username=context.bot.username)
      # إرسال الرد للمستخدم
      await update.message.reply_text(
              response,
              reply_to_message_id=update.message.message_id,
              parse_mode=ParseMode.MARKDOWN,
              reply_markup=markup,
          )
  except Exception as e:
          await update.message.reply_text(
              f"❌️ | `ERROR`",
              reply_to_message_id=update.message.message_id,
              parse_mode=ParseMode.MARKDOWN,
          )






async def audio_command(update: Update, context: CallbackContext) -> None:
    youtube_link = " ".join(context.args)

    if youtube_link:
        try:
            pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
            match = re.search(pattern, youtube_link)
            
            if match:
                youtube_link = match.group(0)
            else:
                user_id = str(update.effective_user.id)
                
                with open("users.json", "r") as user_file:
                    users_data = json.load(user_file)
                
                user_language = users_data.get(user_id, {}).get("language", "en")
                
                with open("translations.json", "r") as file:
                    translations = json.load(file)
                
                user_dict = translations.get(user_language, None)
                
                if user_dict is None:
                    user_dict = translations["en"]
                
                response = user_dict["invalid_link_message"]
                
                await update.message.reply_text(
                    text=response,
                    reply_to_message_id=update.message.message_id,
                    parse_mode=ParseMode.MARKDOWN,
                )
                return
            
            yt = YouTube(youtube_link)
            video_duration = yt.length
            
            if video_duration > audio_max * 60:
                user_id = str(update.effective_user.id)
                
                with open("users.json", "r") as user_file:
                    users_data = json.load(user_file)
                
                user_language = users_data.get(user_id, {}).get("language", "en")
                
                with open("translations.json", "r") as file:
                    translations = json.load(file)
                
                user_dict = translations.get(user_language, None)
                
                if user_dict is None:
                    user_dict = translations["en"]
                
                response = user_dict["long_video_message"]
                response = response.format(audio_max=audio_max)
                
                await update.message.reply_text(
                    text=response,
                    reply_to_message_id=update.message.message_id,
                    parse_mode=ParseMode.MARKDOWN,
                )
                return
            
            stream = yt.streams.filter(only_audio=True).first()
            file_name = f"{str(uuid4())}.mp3"
            file_path = stream.download("temp/", file_name)
            
            await update.message.reply_audio(
                title=yt.title,
                performer=yt.author,
                thumbnail=None,
                audio=open(file_path, "rb")
            )
            
            os.remove(file_path)
        except Exception as e:
            user_id = str(update.effective_user.id)
            
            with open("users.json", "r") as user_file:
                users_data = json.load(user_file)
            
            user_language = users_data.get(user_id, {}).get("language", "en")
            
            with open("translations.json", "r") as file:
                translations = json.load(file)
            
            user_dict = translations.get(user_language, None)
            
            if user_dict is None:
                user_dict = translations["en"]
            
            response = user_dict["error_message"]
            response = response.format(e=e)
            
            await update.message.reply_text(
                text=response,
                reply_to_message_id=update.message.message_id,
                parse_mode=ParseMode.MARKDOWN,
            )
            
            if os.path.exists(file_path):
                os.remove(file_path)
    else:
        pass


async def search(update: Update, context: CallbackContext) -> None:
  youtube_link = " ".join(context.args) # Use the arguments after the command as the input
  try:
      search = Search(youtube_link)
      results = search.results[0:3]
      for result in results: # Loop through the results
          youtube_link = result.watch_url
          yt = YouTube(youtube_link)
          video_title = yt.title
          video_channel = yt.author
          video_views = yt.views
          video_duration = yt.length
          video_thumbnail = yt.thumbnail_url
          video_views_formatted = format_number(video_views)
          video_duration_formatted = format_duration(video_duration)
          # Remove the brackets and their contents from the video title
          video_title_cleaned = re.sub(r"[\[\(].*?[\]\)]", "", video_title)
          video_caption = f"🎬 | [{video_title_cleaned}]({youtube_link})\n👤 | {video_channel}\n👀 | {video_views_formatted}\n⏱️ | {video_duration_formatted}"

          await update.message.reply_photo(
              photo=video_thumbnail,
              caption=video_caption,
              reply_to_message_id=update.message.message_id,
              parse_mode=ParseMode.MARKDOWN,
          )
  except Exception as e:
    await context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, message=f"❌️ | `{e}`", parse_mode=ParseMode.MARKDOWN)
      






async def downloadr(update: Update, context: CallbackContext) -> None:
    youtube_link = " ".join(context.args)
    try:
        pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
        match = re.search(pattern, youtube_link)
        
        if match:
            youtube_link = match.group(0)
        else:
            user_id = str(update.effective_user.id)
            
            with open("users.json", "r") as user_file:
                users_data = json.load(user_file)
            
            user_language = users_data.get(user_id, {}).get("language", "en")
            
            with open("translations.json", "r") as file:
                translations = json.load(file)
            
            user_dict = translations.get(user_language, None)
            
            if user_dict is None:
                user_dict = translations["en"]
            
            response = user_dict["invalid_link_message"]
            
            await update.message.reply_text(
                text=response,
                reply_to_message_id=update.message.message_id,
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        yt = YouTube(youtube_link)
        video_duration = yt.length

        if video_duration > video_max * 60:
            user_id = str(update.effective_user.id)
            
            with open("users.json", "r") as user_file:
                users_data = json.load(user_file)
            
            user_language = users_data.get(user_id, {}).get("language", "en")
            
            with open("translations.json", "r") as file:
                translations = json.load(file)
            
            user_dict = translations.get(user_language, None)
            
            if user_dict is None:
                user_dict = translations["en"]
            
            response = user_dict["long_video_message"]
            response = response.format(video_max=video_max)
            
            await update.message.reply_text(
                text=response,
                reply_to_message_id=update.message.message_id,
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        stream = yt.streams.filter(
            progressive=True, file_extension="mp4").get_lowest_resolution()
        file_name = f"{str(uuid4())}.mp4"
        file_path = stream.download("temp/", file_name, timeout=None)
        video_title = yt.title
        video_channel = yt.author
        video_views = yt.views
        video_thumbnail = yt.thumbnail_url
        video_views_formatted = format_number(video_views)
        video_duration_formatted = format_duration(video_duration)
        video_title_cleaned = re.sub(r"[\[\(].*?[\]\)]", "", video_title)

        user_id = str(update.effective_user.id)
        
        with open("users.json", "r") as user_file:
            users_data = json.load(user_file)
        
        user_language = users_data.get(user_id, {}).get("language", "en")
        
        with open("translations.json", "r") as file:
            translations = json.load(file)
        
        user_dict = translations.get(user_language, None)
        
        if user_dict is None:
            user_dict = translations["en"]
        
        response = user_dict["video_caption"]
        response = response.format(
            video_title_cleaned=video_title_cleaned,
            youtube_link=youtube_link,
            video_channel=video_channel,
            video_views_formatted=video_views_formatted,
            video_duration_formatted=video_duration_formatted
        )
        await update.message.reply_video(
            video=open(file_path, "rb"),
            caption=response,
            reply_to_message_id=update.message.message_id,
            parse_mode=ParseMode.MARKDOWN,
        )
        os.remove(file_path)
    except Exception as e:
        user_id = str(update.effective_user.id)
        
        with open("users.json", "r") as user_file:
            users_data = json.load(user_file)
        
        user_language = users_data.get(user_id, {}).get("language", "en")
        
        with open("translations.json", "r") as file:
            translations = json.load(file)
        
        user_dict = translations.get(user_language, None)
        
        if user_dict is None:
            user_dict = translations["en"]
        
        response = user_dict["error_message"]
        response = response.format(e=e)
        
        await update.message.reply_text(
            text=response,
            reply_to_message_id=update.message.message_id,
            parse_mode=ParseMode.MARKDOWN,
        )
        
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            pass

async def stats_command(update, context):
  # Open the files and load the data
  translations = load_json_file("translations.json")
  users = load_json_file("users.json")

  counts = count_users_by_language(users, translations)
  text = format_counts(counts, translations)

  await update.message.reply_text(text, reply_to_message_id=update.message.message_id, parse_mode=ParseMode.HTML)









async def error_handler(update: object, context: CallbackContext) -> None:
  tb_list = traceback.format_exception(None, context.error,
                                       context.error.__traceback__)
  tb_string = "".join(tb_list)

  update_str = update.to_dict() if isinstance(update, Update) else str(update)
  message = (
      f"<pre>{html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}"
      "</pre>\n\n"
      f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
      f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
      f"<pre>{html.escape(tb_string)}</pre>")

  await context.bot.send_message(chat_id=DEVELOPER_CHAT_ID,
                                 text=message,
                                 parse_mode=ParseMode.HTML)


async def post_init(application: Application):
  await application.bot.set_my_commands([
  BotCommand("/start", "🔄 Restart"),
BotCommand("/audio", "🎧 Download Audio"),
  BotCommand("/video", "📽 Download Video"),
  BotCommand("/search", "🌐 Search on YouTube"),
  BotCommand("/stats", "🏆 Bot Stats"),
  BotCommand("/lang", "⚙️ Change Language"),
  ])


def main() -> None:
  persistence = PicklePersistence(filepath="arbitrarycallbackdatabot")
  application = (Application.builder().token(os.environ.get(
      "BOT_TOKEN")).post_init(post_init).persistence(persistence).build())

  handler_list = [
      CommandHandler("start", start),
      CommandHandler("audio", audio_command),
      CommandHandler("video", downloadr),
    CommandHandler("search", search),
    CommandHandler('lang', lang),
    CommandHandler('stats', stats_command),
    CallbackQueryHandler(button)
  ]
  for handler in handler_list:
    application.add_handler(handler)

  application.add_error_handler(error_handler)
  application.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
  main()
#The code was created and developed by (Saleh) from the "Open Source Tools" team. 
