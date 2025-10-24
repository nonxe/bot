# 🤖 Telegram Bot

A powerful and modern Telegram bot with quality selection features built with Python.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/nonxe/bot)

## ✨ Features

- 🎚️ **Quality Selection**: Choose between Low, Medium, High, and Ultra quality
- 📥 **Link Processing**: Send any media link for processing
- 🎨 **Modern UI**: Clean interface with inline keyboards
- ⚡ **Fast & Efficient**: Built with python-telegram-bot v21.7
- 🔒 **Secure**: Environment-based token management
- 📱 **User-Friendly**: Simple commands and intuitive navigation

## 🚀 Quick Deploy to Heroku

1. Click the "Deploy to Heroku" button above
2. Enter your Telegram Bot Token from [@BotFather](https://t.me/BotFather)
3. Click "Deploy app"
4. Wait for deployment to complete
5. Click "Manage App" and ensure the worker dyno is enabled

## 📋 Manual Setup

### Prerequisites

- Python 3.12.7
- A Telegram Bot Token from [@BotFather](https://t.me/BotFather)

### Local Installation

1. Clone the repository:
```bash
git clone https://github.com/nonxe/bot.git
cd bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set your bot token:
```bash
export TOKEN="your_bot_token_here"
```

4. Run the bot:
```bash
python bot.py
```

## 🛠️ Configuration

### Environment Variables

- `TOKEN` (Required): Your Telegram Bot Token from @BotFather

### Heroku Stack

This bot uses **Heroku-24** stack for optimal performance and security.

## 📦 File Structure

```
bot/
├── bot.py              # Main bot application
├── requirements.txt    # Python dependencies
├── Procfile           # Heroku process configuration
├── runtime.txt        # Python version specification
├── app.json           # Heroku deployment configuration
└── README.md          # Project documentation
```

## 🎮 Bot Commands

- `/start` - Start the bot and see welcome message
- `/help` - Get help and usage instructions
- `/quality` - Select download quality (Low/Medium/High/Ultra)

## 📊 Quality Options

| Quality | Video | Audio |
|---------|-------|-------|
| Low     | 480p  | 128k  |
| Medium  | 720p  | 192k  |
| High    | 1080p | 320k  |
| Ultra   | 4K    | 320k  |

## 🔧 How to Use

1. Start the bot with `/start`
2. Choose your preferred quality with `/quality`
3. Send any media link
4. Bot will process and respond

## 📝 Dependencies

- `python-telegram-bot==21.7` - Telegram Bot API wrapper
- `aiohttp==3.11.10` - Async HTTP client
- `certifi==2024.8.30` - SSL certificates
- `charset-normalizer==3.4.0` - Character encoding detection
- `idna==3.10` - International domain names support
- `multidict==6.1.0` - Multi-key dictionaries
- `propcache==0.2.0` - Property caching
- `yarl==1.17.2` - URL parsing and manipulation

## 🌟 Features to Implement

You can extend this bot by adding:

- Media download functionality (yt-dlp integration)
- File upload/sharing capabilities
- Database for user preferences
- Admin panel
- Statistics tracking
- Custom filters and handlers

## ⚠️ Important Notes

### Heroku Deployment
- Make sure to enable the **worker** dyno (not web dyno)
- The bot runs on Heroku-24 stack
- Free tier available with Eco dynos

### Getting Bot Token
1. Open [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`
3. Follow the instructions
4. Copy the token and use it in deployment

## 🐛 Troubleshooting

### Bot Not Responding
- Check if the worker dyno is enabled in Heroku
- Verify the TOKEN environment variable is set correctly
- Check Heroku logs: `heroku logs --tail -a your-app-name`

### Dependencies Issues
- Ensure you're using Python 3.12.7
- Run `pip install -r requirements.txt` again
- Clear pip cache: `pip cache purge`

## 📄 License

This project is open source and available for personal and commercial use.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

## 💬 Support

For support, open an issue in the GitHub repository or contact the maintainer.

## 🔗 Links

- [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
- [python-telegram-bot Documentation](https://docs.python-telegram-bot.org/)
- [Heroku Documentation](https://devcenter.heroku.com/)

---

Made with ❤️ for the Telegram community
