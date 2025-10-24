import os
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Quality settings for yt-dlp
QUALITY_FORMATS = {
    'low': 'worst[height<=480]',
    'medium': 'best[height<=720]',
    'high': 'best[height<=1080]',
    'ultra': 'best'
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    welcome_message = (
        f"👋 Welcome {user.mention_html()}!\n\n"
        "🤖 I'm your Video Downloader Bot!\n\n"
        "📋 Available Commands:\n"
        "/start - Start the bot\n"
        "/help - Get help\n"
        "/quality - Choose download quality\n\n"
        "📹 Send me a YouTube/video link to download!"
    )
    await update.message.reply_html(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "🆘 <b>How to use this bot:</b>\n\n"
        "1️⃣ Use /quality to select your preferred quality\n"
        "2️⃣ Send me a video link\n"
        "3️⃣ I'll download and send it to you\n\n"
        "✅ <b>Best Working Platforms:</b>\n"
        "• Twitter/X 🐦\n"
        "• Facebook 📘\n"
        "• TikTok 🎵\n"
        "• Reddit 🤖\n"
        "• Vimeo 🎬\n"
        "• Dailymotion 📺\n"
        "• Twitch Clips 🎮\n"
        "• Streamable 📹\n"
        "• And 900+ more!\n\n"
        "⚠️ <b>May require login (limited):</b>\n"
        "• YouTube (some videos)\n"
        "• Instagram (some posts)\n\n"
        "⚙️ Current quality: <b>{}</b>\n\n"
        "💡 <i>Tip: Most platforms work perfectly!</i>"
    )
    current_quality = context.user_data.get('quality', 'medium')
    await update.message.reply_html(help_text.format(current_quality.upper()))

async def quality_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show quality selection keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("📉 Low (480p)", callback_data='quality_low'),
            InlineKeyboardButton("📊 Medium (720p)", callback_data='quality_medium')
        ],
        [
            InlineKeyboardButton("📈 High (1080p)", callback_data='quality_high'),
            InlineKeyboardButton("🎯 Ultra (Best)", callback_data='quality_ultra')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    current_quality = context.user_data.get('quality', 'medium')
    await update.message.reply_text(
        f"🎚️ <b>Select Quality</b>\n\nCurrent: <b>{current_quality.upper()}</b>",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def quality_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle quality selection callback."""
    query = update.callback_query
    await query.answer()
    
    quality = query.data.replace('quality_', '')
    context.user_data['quality'] = quality
    
    quality_names = {
        'low': '480p',
        'medium': '720p',
        'high': '1080p',
        'ultra': 'Best Available'
    }
    
    await query.edit_message_text(
        text=f"✅ Quality set to: <b>{quality.upper()}</b>\n\n"
             f"📹 Resolution: {quality_names[quality]}\n\n"
             f"Now send me a video link to download!",
        parse_mode='HTML'
    )

async def download_video(url: str, quality: str) -> dict:
    """Download video using yt-dlp with YouTube-specific fixes."""
    format_string = QUALITY_FORMATS.get(quality, 'best[height<=720]')
    
    ydl_opts = {
        'format': f'{format_string}/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': False,
        'no_warnings': False,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android_creator', 'android_embedded', 'android_music', 'android_vr', 'ios', 'mweb'],
                'skip': ['hls', 'dash'],
            }
        },
        'http_headers': {
            'User-Agent': 'com.google.android.youtube/19.09.37 (Linux; U; Android 11) gzip',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'X-YouTube-Client-Name': '14',
            'X-YouTube-Client-Version': '19.09.37',
        },
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if not filename.endswith('.mp4'):
                filename = filename.rsplit('.', 1)[0] + '.mp4'
            
            return {
                'success': True,
                'filename': filename,
                'title': info.get('title', 'Video'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', None)
            }
    except Exception as e:
        logger.error(f"Download error: {e}")
        return {
            'success': False,
            'error': str(e)
        }

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user messages (video links)."""
    user_message = update.message.text
    quality = context.user_data.get('quality', 'medium')
    
    if not (user_message.startswith('http://') or user_message.startswith('https://')):
        await update.message.reply_text(
            "❌ Please send a valid URL starting with http:// or https://\n\n"
            "Use /help for more information."
        )
        return
    
    # Send initial processing message
    processing_msg = await update.message.reply_html(
        f"🔄 <b>Processing YouTube video...</b>\n\n"
        f"Quality: <b>{quality.upper()}</b>\n\n"
        f"⏳ Please wait 30-60 seconds..."
    )
    
    try:
        # Create downloads directory if it doesn't exist
        os.makedirs('downloads', exist_ok=True)
        
        # Download the video
        result = await asyncio.get_event_loop().run_in_executor(
            None, lambda: asyncio.run(download_video(user_message, quality))
        )
        
        if not result['success']:
            error_msg = result['error'].lower()
            
            if 'bot' in error_msg or 'sign in' in error_msg:
                await processing_msg.edit_text(
                    f"❌ <b>YouTube blocked this video</b>\n\n"
                    f"Try another YouTube video.\n"
                    f"Some videos work, some don't.\n\n"
                    f"Error: <code>{result['error'][:200]}</code>",
                    parse_mode='HTML'
                )
            else:
                await processing_msg.edit_text(
                    f"❌ <b>Download failed</b>\n\n"
                    f"Error: <code>{result['error'][:300]}</code>",
                    parse_mode='HTML'
                )
            return
        
        # Update message
        await processing_msg.edit_text(
            f"📤 <b>Uploading video...</b>\n\n"
            f"Title: <b>{result['title']}</b>\n"
            f"Quality: <b>{quality.upper()}</b>",
            parse_mode='HTML'
        )
        
        # Send the video file
        with open(result['filename'], 'rb') as video_file:
            await update.message.reply_video(
                video=video_file,
                caption=f"🎬 <b>{result['title']}</b>\n\n"
                        f"Quality: <b>{quality.upper()}</b>\n"
                        f"Downloaded by @{context.bot.username}",
                parse_mode='HTML',
                supports_streaming=True,
                read_timeout=300,
                write_timeout=300
            )
        
        # Delete processing message and file
        await processing_msg.delete()
        
        # Clean up downloaded file
        try:
            os.remove(result['filename'])
        except:
            pass
            
        logger.info(f"Successfully sent video: {result['title']}")
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await processing_msg.edit_text(
            f"❌ <b>An error occurred!</b>\n\n"
            f"Error: <code>{str(e)}</code>\n\n"
            f"Please try again or contact support.",
            parse_mode='HTML'
        )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

def main() -> None:
    """Start the bot."""
    # Get token from environment variable
    token = os.environ.get('TOKEN')
    
    if not token:
        logger.error("No TOKEN found in environment variables!")
        return
    
    # Create the Application
    application = Application.builder().token(token).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("quality", quality_command))
    application.add_handler(CallbackQueryHandler(quality_callback, pattern='^quality_'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
