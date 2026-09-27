import os
import sys
from urllib.parse import urlparse
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.scraper import check_product
from db.crud import DatabaseManager

# Load environment variables
load_dotenv()

# Initialize database (use same DB as scheduler)
# Will use DATABASE_URL if set (Render), otherwise SQLite
db = DatabaseManager()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the /start command is issued."""
    welcome_message = """
🤖 *Stock Alert Bot*

Welcome! I can help you track product prices and stock availability from supported e-commerce sites.

*Available Commands:*
/track `<url>` - Start tracking a product
/list - Show your tracked products
/untrack `<url>` - Stop tracking a product
/start - Show this welcome message

*How it works:*
1. Send me a product URL from a supported site
2. I'll check the current price and availability
3. You'll be notified when the price drops or the item comes back in stock

*Note:* Currently supports demo e-commerce sites for testing purposes.
"""
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def track(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Track a product URL."""
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "❌ Please provide a URL.\n"
            "Usage: /track <url>"
        )
        return
    
    url = context.args[0]
    chat_id = str(update.effective_chat.id)
    
    # Validate URL format
    try:
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            await update.message.reply_text(
                "❌ Invalid URL format.\n"
                "Please provide a complete URL including http:// or https://"
            )
            return
    except Exception as e:
        await update.message.reply_text(f"❌ Invalid URL: {e}")
        return
    
    await update.message.reply_text("🔍 Checking product...")
    
    # Scrape the product
    try:
        product_info = check_product(url)
    except Exception as e:
        await update.message.reply_text(
            f"❌ Failed to scrape product: {str(e)}\n"
            "The site might be unsupported or temporarily unavailable."
        )
        return
    
    # Check if scraping returned valid data
    if not product_info['title']:
        await update.message.reply_text(
            "❌ Could not extract product information.\n"
            "This site might not be supported yet."
        )
        return
    
    # Save product to database
    try:
        product = db.add_product_if_new(url, title=product_info['title'])
        
        # Update product status with scraped data
        db.update_product_status(
            product.id,
            price=product_info['price'],
            in_stock=product_info['in_stock']
        )
        
        # Subscribe user to product
        subscription = db.subscribe(chat_id, product.id)
        
        # Send success message with product details
        price_text = f"£{product_info['price']}" if product_info['price'] else "N/A"
        stock_text = "✅ In Stock" if product_info['in_stock'] else "❌ Out of Stock"
        
        success_message = f"""
✅ *Product Added to Tracking*

📦 *Title:* {product_info['title']}
💰 *Price:* {price_text}
📊 *Stock:* {stock_text}
🔗 *URL:* {url}

You'll be notified when the price drops or this item comes back in stock!
"""
        await update.message.reply_text(success_message, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Database error: {str(e)}")


async def list_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all products tracked by the user."""
    chat_id = str(update.effective_chat.id)
    
    # Get all products
    all_products = db.get_all_products()
    
    # Filter products that the user is subscribed to
    user_products = []
    for product in all_products:
        subscribers = db.get_subscribers_for_product(product.id)
        if chat_id in subscribers:
            user_products.append(product)
    
    if not user_products:
        await update.message.reply_text(
            "📭 You're not tracking any products yet.\n"
            "Use /track <url> to start tracking a product."
        )
        return
    
    # Build list message
    list_message = "📋 *Your Tracked Products*\n\n"
    
    for idx, product in enumerate(user_products, 1):
        price_text = f"£{product.last_price}" if product.last_price else "N/A"
        stock_text = "✅" if product.in_stock else "❌"
        
        list_message += f"{idx}. *{product.title}*\n"
        list_message += f"   💰 Price: {price_text}\n"
        list_message += f"   📊 Stock: {stock_text}\n"
        list_message += f"   🔗 {product.url}\n\n"
    
    await update.message.reply_text(list_message, parse_mode='Markdown')


async def untrack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Unsubscribe from a product URL."""
    if not context.args or len(context.args) < 1:
        await update.message.reply_text(
            "❌ Please provide a URL.\n"
            "Usage: /untrack <url>"
        )
        return
    
    url = context.args[0]
    chat_id = str(update.effective_chat.id)
    
    # Find product by URL
    product = db.get_product_by_url(url)
    
    if not product:
        await update.message.reply_text(
            "❌ Product not found in tracking list.\n"
            "Use /list to see your tracked products."
        )
        return
    
    # Unsubscribe user
    success = db.unsubscribe(chat_id, product.id)
    
    if success:
        await update.message.reply_text(
            f"✅ Unsubscribed from: {product.title}\n"
            f"You'll no longer receive notifications for this product."
        )
    else:
        await update.message.reply_text(
            "❌ You were not subscribed to this product."
        )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    print(f"Update {update} caused error {context.error}")


def create_application() -> Application:
    """Create and configure the Telegram bot application (for use in main.py)."""
    # Get bot token from environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set.")
        print("Please set it in your .env file or environment variables.")
        return None
    
    # Create the Application
    application = Application.builder().token(token).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("track", track))
    application.add_handler(CommandHandler("list", list_products))
    application.add_handler(CommandHandler("untrack", untrack))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    return application


def main() -> None:
    """Start the bot."""
    application = create_application()
    
    if not application:
        return
    
    # Start the bot
    print("🤖 Bot started successfully!")
    print("Press Ctrl+C to stop the bot.")
    
    # Run the bot until you press Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
