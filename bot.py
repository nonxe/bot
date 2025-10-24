import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Quality settings
QUALITY_SETTINGS = {
    'low': {'video': '480p', 'audio': '128k'},
    'medium': {'video': '720p', 'audio': '192k'},
    'high': {'video': '1080p', 'audio': '320k'},
    'ultra': {'video': '4K', 'audio': '320k'}
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    welcome_message = (
        f"👋 Welcome {user.mention_html()}!\n\n"
        "🤖 I'm your Telegram Bot!\n\n"
        "📋 Available Commands:\n"
        "/start - Start the bot\n"
        "/help - Get help\n"
        "/quality - Choose download quality\n\n"
        "Send me a link to download!"
    )
    await update.message.reply_html(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "🆘 <b>How to use this bot:</b>\n\n"
        "1️⃣ Use /quality to select your preferred quality\n"
        "2️⃣ Send me any media link\n"
        "3️⃣ I'll process and send it to you\n\n"
        "💡 <b>Supported formats:</b>\n"
        "• Videos (YouTube, etc.)\n"
        "• Audio files\n"
        "• Multiple quality options\n\n"
        "⚙️ Current quality: <b>{}</b>"
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
            InlineKeyboardButton("🎯 Ultra (4K)", callback_data='quality_ultra')
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
    
    settings = QUALITY_SETTINGS[quality]
    await query.edit_message_text(
        text=f"✅ Quality set to: <b>{quality.upper()}</b>\n\n"
             f"📹 Video: {settings['video']}\n"
             f"🎵 Audio: {settings['audio']}\n\n"
             f"Now send me a link to download!",
        parse_mode='HTML'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user messages (links)."""
    user_message = update.message.text
    quality = context.user_data.get('quality', 'medium')
    
    if user_message.startswith('http://') or user_message.startswith('https://'):
        await update.message.reply_text(
            f"🔄 Processing your link...\n\n"
            f"Quality: <b>{quality.upper()}</b>\n"
            f"Link: <code>{user_message}</code>\n\n"
            f"⏳ Please wait...",
            parse_mode='HTML'
        )
        
        # Here you would add your download logic
        # For now, just confirming receipt
        await update.message.reply_text(
            "✅ Link received!\n\n"
            "🚧 Download functionality ready to be implemented.\n"
            "You can integrate yt-dlp or other downloaders here."
        )
    else:
        await update.message.reply_text(
            "❌ Please send a valid URL starting with http:// or https://\n\n"
            "Use /help for more information."
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
