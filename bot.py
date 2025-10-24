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
    """Download video using yt-dlp."""
    format_string = QUALITY_FORMATS.get(quality, 'best[height<=720]')
    
    ydl_opts = {
        'format': f'{format_string}/best',
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'nocheckcertificate': True,
        'prefer_ffmpeg': True,
        'merge_output_format': 'mp4',
        # Anti-bot bypass options
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'referer': 'https://www.google.com/',
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'player_skip': ['webpage', 'configs'],
            }
        },
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Accept-Encoding': 'gzip,deflate',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
            'Referer': 'https://www.google.com/',
        },
        'age_limit': None,
        'geo_bypass': True,
        'extractor_retries': 3,
        'fragment_retries': 10,
        'skip_unavailable_fragments': True,
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            # Handle extension conversion
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
        f"🔄 <b>Processing your link...</b>\n\n"
        f"Quality: <b>{quality.upper()}</b>\n"
        f"Link: <code>{user_message}</code>\n\n"
        f"⏳ Please wait, downloading..."
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
            
            # Check specific error types
            if 'login' in error_msg or 'cookies' in error_msg or 'sign in' in error_msg:
                await processing_msg.edit_text(
                    f"⚠️ <b>Authentication Required</b>\n\n"
                    f"This video requires login/cookies.\n\n"
                    f"<b>Solutions:</b>\n"
                    f"1️⃣ Try a different video (most work without cookies)\n"
                    f"2️⃣ Check if video is public\n"
                    f"3️⃣ For Instagram: Use public posts only\n"
                    f"4️⃣ For YouTube: Most videos work, try another\n\n"
                    f"💡 <b>Working platforms without cookies:</b>\n"
                    f"• Twitter/X ✅\n"
                    f"• Facebook ✅\n"
                    f"• TikTok ✅\n"
                    f"• Reddit ✅\n"
                    f"• Vimeo ✅\n"
                    f"• And 900+ more sites!\n\n"
                    f"<i>Error: {result['error'][:100]}...</i>",
                    parse_mode='HTML'
                )
            elif 'rate' in error_msg or 'limit' in error_msg:
                await processing_msg.edit_text(
                    f"⏳ <b>Rate Limit Reached</b>\n\n"
                    f"The platform has temporarily blocked requests.\n\n"
                    f"<b>Please try:</b>\n"
                    f"• Wait 5-10 minutes and try again\n"
                    f"• Use a different platform\n"
                    f"• Try another video\n\n"
                    f"This is temporary! 😊",
                    parse_mode='HTML'
                )
            elif 'not available' in error_msg or 'unavailable' in error_msg:
                await processing_msg.edit_text(
                    f"❌ <b>Video Not Available</b>\n\n"
                    f"This video might be:\n"
                    f"• Deleted or private\n"
                    f"• Region-blocked\n"
                    f"• Age-restricted\n"
                    f"• Temporarily unavailable\n\n"
                    f"Please try another video!",
                    parse_mode='HTML'
                )
            else:
                await processing_msg.edit_text(
                    f"❌ <b>Download failed!</b>\n\n"
                    f"<b>Try these platforms that work best:</b>\n"
                    f"• Twitter/X ✅\n"
                    f"• Facebook ✅\n"
                    f"• TikTok ✅\n"
                    f"• Reddit ✅\n\n"
                    f"<i>Error: {result['error'][:150]}...</i>",
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
