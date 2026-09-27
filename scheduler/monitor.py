import os
import sys
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import requests

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.scraper import check_product
from db.crud import DatabaseManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize database (use same DB as bot)
# Will use DATABASE_URL if set (Render), otherwise SQLite
db = DatabaseManager()

# Get bot token for sending messages
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')


def send_telegram_message(chat_id: str, message: str) -> bool:
    """Send a message via Telegram Bot API."""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set")
        return False
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(f"Message sent to chat_id {chat_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send message to {chat_id}: {e}")
        return False


def check_and_alert_products():
    """Check all products and send alerts for price drops or back-in-stock."""
    logger.info("=" * 50)
    logger.info("Starting product check cycle")
    logger.info("=" * 50)
    
    products = db.get_all_products()
    logger.info(f"Found {len(products)} products to check")
    
    for product in products:
        logger.info(f"Checking product: {product.title} (ID: {product.id})")
        
        try:
            # Scrape current product data
            product_info = check_product(product.url)
            
            if not product_info['title']:
                logger.warning(f"Could not scrape product {product.url}")
                continue
            
            # Compare with stored values
            old_price = product.last_price
            old_in_stock = product.in_stock
            new_price = product_info['price']
            new_in_stock = product_info['in_stock']
            
            logger.info(f"Old price: {old_price}, New price: {new_price}")
            logger.info(f"Old stock: {old_in_stock}, New stock: {new_in_stock}")
            
            # Check for price drop
            price_dropped = False
            if old_price is not None and new_price is not None:
                price_dropped = new_price < old_price
            
            # Check for back in stock
            back_in_stock = False
            if old_in_stock is False and new_in_stock is True:
                back_in_stock = True
            
            # Send alerts if conditions met
            if price_dropped or back_in_stock:
                subscribers = db.get_subscribers_for_product(product.id)
                logger.info(f"Found {len(subscribers)} subscribers for product {product.id}")
                
                if price_dropped:
                    message = f"""
🔔 *Price Drop Alert!*

📦 *{product_info['title']}*
💰 *New Price:* £{new_price}
📉 *Was:* £{old_price}
🔗 {product.url}
"""
                    logger.info(f"Price drop detected: £{old_price} -> £{new_price}")
                
                elif back_in_stock:
                    message = f"""
✅ *Back in Stock Alert!*

📦 *{product_info['title']}*
💰 *Price:* £{new_price if new_price else 'N/A'}
🔗 {product.url}
"""
                    logger.info(f"Back in stock detected for {product.title}")
                
                # Send message to all subscribers
                for chat_id in subscribers:
                    send_telegram_message(chat_id, message)
            
            # Update database with new values
            db.update_product_status(
                product.id,
                price=new_price,
                in_stock=new_in_stock
            )
            logger.info(f"Updated product {product.id} in database")
            
        except Exception as e:
            logger.error(f"Error checking product {product.id}: {e}")
            continue
    
    logger.info("=" * 50)
    logger.info("Product check cycle completed")
    logger.info("=" * 50)


def start_scheduler():
    """Start the background scheduler."""
    scheduler = BackgroundScheduler()
    
    # Schedule job to run every 10 minutes
    scheduler.add_job(
        check_and_alert_products,
        'interval',
        minutes=10,
        id='product_monitor',
        name='Product Price and Stock Monitor',
        replace_existing=True
    )
    
    logger.info("Starting scheduler - will check products every 10 minutes")
    scheduler.start()
    
    return scheduler


if __name__ == '__main__':
    # For testing the scheduler independently
    logger.info("Running single check cycle for testing...")
    check_and_alert_products()
