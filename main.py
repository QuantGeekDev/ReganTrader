from core_bot_engine.core_bot_engine import CoreBotEngine


# Remove API KEYs from Prod
API_KEY = "PKGUF4JBS4CNZDCNDLP8"
SECRET_KEY = "9DgYQ5rU1pmz4Bqgjb0acGzq6hOPGi8fBc44gL1m"


def main():
    bot = CoreBotEngine()
    bot.start_trading()

if __name__ == "__main__":
    main()
