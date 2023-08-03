import logging
from database_manager.database_manager import DatabaseManager
from configuration_manager.configuration_manager import ConfigurationManager
from ui_server.ui_server import app  # Import the Flask application
from core_bot_engine.core_bot_engine import CoreBotEngine

def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    db_manager = DatabaseManager()
    config_manager = ConfigurationManager(db_manager)
    bot = CoreBotEngine(config_manager, db_manager)

    # Start the Flask application
    app.run(host='127.0.0.1', port=5000)

if __name__ == "__main__":
    main()
