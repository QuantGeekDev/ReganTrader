import logging
from ui_server.ui_server import app  # Import the Flask application


def main():
    logging.basicConfig(level=logging.INFO)
    # Start the Flask application
    app.run(host='127.0.0.1', port=5000)


if __name__ == "__main__":
    main()
