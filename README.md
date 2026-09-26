# Stock Alert Bot

A Python Telegram bot for monitoring e-commerce product pages for price drops and back-in-stock status.

## 🎯 Project Goal

This bot periodically checks product pages from supported e-commerce sites and sends you Telegram alerts when:
- A product's price drops
- An out-of-stock product becomes available again

## 🏗️ Architecture

```
┌─────────────────┐
│  Telegram Bot   │
│  (Commands)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Bot Layer     │
│  /track, /list  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Database      │
│  (Products,     │
│   Subscribers)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Scheduler     │
│  (Every 10min)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Scraper       │
│  (Requests +    │
│   BeautifulSoup)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  E-commerce     │
│  Sites          │
└─────────────────┘
```

## ✨ Features

- **Telegram Integration**: Easy-to-use bot commands for tracking products
- **Pluggable Architecture**: Easy to add support for new e-commerce sites
- **Smart Alerts**: Only notifies on price drops or back-in-stock events
- **Background Monitoring**: Automatic checks every 10 minutes
- **Database Persistence**: SQLite for local dev, PostgreSQL for production
- **Multiple Site Support**: Domain-specific parsers for different e-commerce platforms

## 📁 Project Structure

```
stock-alert-bot/
├── bot/
│   ├── __init__.py
│   └── bot.py              # Telegram bot commands and handlers
├── db/
│   ├── __init__.py
│   ├── models.py           # SQLAlchemy database models
│   ├── crud.py             # Database operations
│   └── test_db.py          # Database testing
├── scheduler/
│   ├── __init__.py
│   └── monitor.py          # Background monitoring job
├── scraper/
│   ├── __init__.py
│   ├── scraper.py          # Web scraping logic with pluggable parsers
│   └── test_sites.py       # Scraper testing
├── main.py                 # Single entrypoint (bot + scheduler)
├── Procfile                # Railway deployment configuration
├── runtime.txt             # Python version specification
├── requirements.txt        # Pinned Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore patterns
└── README.md              # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Telegram account
- Git (for deployment)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/stock-alert-bot.git
   cd stock-alert-bot
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your TELEGRAM_BOT_TOKEN
   ```

5. **Run the bot**
   ```bash
   python main.py
   ```

## 🤖 Getting a Telegram Bot Token

### Step 1: Start a conversation with BotFather
1. Open Telegram and search for **@BotFather**
2. Start a chat with BotFather
3. Send the command `/newbot`

### Step 2: Create your bot
1. BotFather will ask for a **name** for your bot (e.g., "Stock Alert Bot")
2. Then choose a **username** for your bot (must end in `bot`, e.g., "stock_alert_bot" or "my_stock_bot")

### Step 3: Get your token
1. BotFather will provide you with a **token** that looks like:
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
2. **Copy this token** and add it to your `.env` file:
   ```env
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

## 📱 Bot Commands

- `/start` - Show welcome message and instructions
- `/track <url>` - Start tracking a product URL
- `/list` - Show all products you're currently tracking
- `/untrack <url>` - Stop tracking a product

## 🧪 Testing

### Test the scraper independently
```bash
python scraper/test_sites.py
```

### Test the database layer
```bash
python db/test_db.py
```

### Simulate a price drop for testing
```bash
python simulate_price_drop.py
```

### Test the scheduler independently
```bash
python scheduler/monitor.py
```

## 🌐 Deploying to Railway

### Option 1: Using Railway CLI

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize Railway project**
   ```bash
   railway init
   ```

4. **Deploy**
   ```bash
   railway up
   ```

5. **Set environment variables**
   ```bash
   railway variables set TELEGRAM_BOT_TOKEN=your_token_here
   ```

### Option 2: Using Railway Dashboard (Click-by-Click)

1. **Go to [Railway.app](https://railway.app)** and sign up/login

2. **Create a new project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"

3. **Connect your GitHub repository**
   - Click "Install GitHub App" if needed
   - Select your `stock-alert-bot` repository
   - Click "Deploy Now"

4. **Add environment variables**
   - Go to your project → Variables tab
   - Add `TELEGRAM_BOT_TOKEN` with your bot token
   - Railway will automatically provide `DATABASE_URL` for PostgreSQL

5. **Monitor deployment**
   - Watch the deployment logs in the "Deployments" tab
   - Once deployed, you'll see a live URL

6. **Test the deployed bot**
   - Send `/start` to your bot in Telegram
   - Try tracking a product with `/track <url>`

### Railway Environment Variables

Required:
- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token from BotFather

Automatically provided by Railway:
- `DATABASE_URL` - PostgreSQL connection string (Railway provides this)
- `PORT` - Port for the web service

## 🔧 Configuration

### Database Configuration

**Local Development (SQLite)**:
- By default, the bot uses SQLite (`stock_alerts.db`)
- No additional configuration needed

**Production (PostgreSQL)**:
- Railway automatically provides PostgreSQL
- Set `DATABASE_URL` environment variable
- The bot will automatically use PostgreSQL when `DATABASE_URL` is present

### Adding Support for New E-commerce Sites

To add support for a new e-commerce domain:

1. **Create a parser function** in `scraper/scraper.py`:
   ```python
   def parse_your_domain(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
       # Extract title, price, and in_stock status
       title_elem = soup.find('h1', class_='product-title')
       title = title_elem.text.strip() if title_elem else ''
       
       price_elem = soup.find('span', class_='price')
       price = None
       if price_elem:
           price_text = price_elem.text.strip()
           # Parse price text to float
           price = float(price_text.replace('$', '').replace(',', ''))
       
       stock_elem = soup.find('div', class_='stock-status')
       in_stock = False
       if stock_elem:
           in_stock = 'in stock' in stock_elem.text.lower()
       
       return {'price': price, 'in_stock': in_stock, 'title': title}
   ```

2. **Register it** in the `DOMAIN_PARSERS` dictionary:
   ```python
   DOMAIN_PARSERS = {
       'your-domain.com': parse_your_domain,
       'books.toscrape.com': parse_books_toscrape,
   }
   ```

## 📝 Development Workflow

1. **Make changes** to the code
2. **Test locally** with `python main.py`
3. **Commit changes** with descriptive messages
4. **Push to GitHub**
5. **Railway auto-deploys** on push

## 🐛 Troubleshooting

### Bot doesn't respond
- Check that `TELEGRAM_BOT_TOKEN` is set correctly
- Verify the bot token is valid (try sending a message via BotFather)
- Check Railway logs for errors

### Database connection issues
- Ensure `DATABASE_URL` is set in Railway
- Check Railway PostgreSQL service is running
- Verify database schema is created correctly

### Scraper fails to extract data
- The website structure may have changed
- Check if the site is still accessible
- Update the domain-specific parser function

## 📄 License

This project is open source and available for educational purposes.

## ⚠️ Important Notes

- This project uses public demo/sandbox e-commerce sites for testing purposes
- It does not scrape real production e-commerce sites due to anti-bot protections and Terms of Service restrictions
- Always respect robots.txt and website terms of service when adding new site support
- Use responsibly and ethically

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions, please open an issue on GitHub.
