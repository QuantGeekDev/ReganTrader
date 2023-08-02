import logging
from core_bot_engine.core_bot_engine import CoreBotEngine
from database_manager.database_manager import DatabaseManager
from configuration_manager.configuration_manager import ConfigurationManager


def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    db_manager = DatabaseManager()
    config_manager = ConfigurationManager(db_manager)

    bot = None  # Initialize bot to None

    try:
        bot = CoreBotEngine(config_manager)
        bot.start_trading()
    except Exception as e:
        logger.error(f"An error occurred while trading: {e}", exc_info=True)
        if bot is not None:  # Only call stop_trading() if bot was successfully initialized
            bot.stop_trading()
    finally:
        logger.info("Bot has stopped trading.")


if __name__ == "__main__":
    main()
