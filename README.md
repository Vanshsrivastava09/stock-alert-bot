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
- **Health Checks**: Flask-based health endpoint for deployment monitoring

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
├── main.py                 # Single entrypoint (bot + scheduler + Flask health check)
├── Dockerfile             # Docker configuration for Fly.io
├── fly.toml               # Fly.io deployment configuration
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

## 🌐 Deploying to Fly.io (Free)

Fly.io offers a generous free tier that's perfect for hosting Telegram bots with background processes.

### Step 1: Install Fly.io CLI

1. **Download Fly.io CLI** from [fly.io/docs/hands-on/install-flyctl/](https://fly.io/docs/hands-on/install-flyctl/)
2. **For Windows:** Download the installer or use:
   ```bash
   powershell -c "iwr https://fly.io/install.ps1 -useb | iex"
   ```

### Step 2: Sign up and Login

1. **Sign up** at [fly.io](https://fly.io)
2. **Login** to your account:
   ```bash
   flyctl auth login
   ```

### Step 3: Create PostgreSQL Database

1. **Create a new PostgreSQL database:**
   ```bash
   flyctl postgres create --name stock-alert-db
   ```

2. **Copy the connection string** provided by Fly.io (it will look like: `postgres://user:password@host:port/database`)

### Step 4: Deploy the Application

1. **Initialize the app:**
   ```bash
   flyctl launch
   ```

2. **Follow the prompts:**
   - Enter an app name (e.g., `stock-alert-bot`)
   - Select a region (choose closest to you)
   - Skip creating a database (we already created one)
   - Skip deploying for now

3. **Attach the database:**
   ```bash
   flyctl postgres attach -a stock-alert-bot stock-alert-db
   ```

4. **Set environment variables:**
   ```bash
   flyctl secrets set TELEGRAM_BOT_TOKEN=your_bot_token_here -a stock-alert-bot
   ```

5. **Deploy the app:**
   ```bash
   flyctl deploy -a stock-alert-bot
   ```

### Step 5: Monitor and Test

1. **Check deployment status:**
   ```bash
   flyctl status -a stock-alert-bot
   ```

2. **View logs:**
   ```bash
   flyctl logs -a stock-alert-bot
   ```

3. **Test the bot** by sending `/start` in Telegram

### Fly.io Free Tier Benefits

- **Free:** Up to 3 VMs with 256MB RAM each
- **Always On:** Apps run 24/7 (no sleep)
- **Global:** Deploy to multiple regions
- **Database:** Free PostgreSQL instance (1GB)
- **Background Processes:** Perfect for schedulers

### Alternative: Replit (Simpler)

If Fly.io seems complex, you can also use Replit:

1. Go to [replit.com](https://replit.com)
2. Create a new Python Repl
3. Import your GitHub repository
4. Add `TELEGRAM_BOT_TOKEN` in Secrets
5. Run `python main.py`
6. Click "Keep Always On" in the top-right corner

### Database Configuration

**Local Development (SQLite)**:
- By default, the bot uses SQLite (`stock_alerts.db`)
- No additional configuration needed

**Production (PostgreSQL)**:
- Fly.io automatically provides PostgreSQL
- Set `DATABASE_URL` environment variable
- The bot will automatically use PostgreSQL when `DATABASE_URL` is present

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
5. **Deploy to Fly.io** (free tier)

## 🐛 Troubleshooting

### Bot doesn't respond
- Check that `TELEGRAM_BOT_TOKEN` is set correctly
- Verify the bot token is valid (try sending a message via BotFather)
- Check Fly.io logs: `flyctl logs -a stock-alert-bot`

### Database connection issues
- Ensure `DATABASE_URL` is set in Fly.io secrets
- Check Fly.io PostgreSQL service is running
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
