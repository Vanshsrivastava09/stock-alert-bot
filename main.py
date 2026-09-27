import os
import sys
import logging
import signal
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.bot import create_application
from scheduler.monitor import start_scheduler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    logger.info("Shutting down...")
    sys.exit(0)


def main():
    """Main entry point - starts both bot and scheduler."""
    # Register signal handlers for graceful shutdown (platform-specific)
    try:
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    except (AttributeError, ValueError):
        # Windows may not have SIGTERM or may raise ValueError for signal handling
        pass
    
    logger.info("🚀 Starting Stock Alert Bot...")
    
    # Check for bot token
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN environment variable not set.")
        logger.error("Please set it in your .env file or environment variables.")
        return
    
    # Start the background scheduler
    logger.info("📅 Starting background scheduler...")
    scheduler = start_scheduler()
    
    # Create and start the bot application
    logger.info("🤖 Starting Telegram bot...")
    application = create_application()
    
    if not application:
        logger.error("❌ Failed to create bot application")
        return
    
    # Run the bot
    logger.info("✅ Bot and scheduler started successfully!")
    logger.info("📊 Scheduler will check products every 10 minutes")
    logger.info("Press Ctrl+C to stop")
    
    try:
        application.run_polling(allowed_updates=None)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    finally:
        if scheduler:
            scheduler.shutdown()
        logger.info("👋 Shutdown complete")


if __name__ == '__main__':
    main()
