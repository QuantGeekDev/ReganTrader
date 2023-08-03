from flask import Flask, render_template, request, flash, redirect, url_for
from database_manager.database_manager import DatabaseManager
from configuration_manager.configuration_manager import ConfigurationManager
from core_bot_engine.core_bot_engine import CoreBotEngine
import threading
from strategy_manager.strategy_manager import StrategyManager

# Create the Flask app instance
app = Flask(__name__)
app.secret_key = 'unpredictablekey'  # This should be a secure, unpredictable key

# Create the db_manager instance inside the app context
with app.app_context():
    db_manager = DatabaseManager()
    app.config_manager = ConfigurationManager(db_manager)
    app.bot = None


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        bot_action = request.form.get('bot_action')
        user_config = app.config_manager.get_config('user_config')
        if not user_config or not user_config.get('api_key') or not user_config.get('api_secret'):
            flash('API Key and Secret are required!', 'error')
            return redirect(url_for('settings'))
        if bot_action == 'start':
            if app.bot is None:
                app.bot = CoreBotEngine(app.config_manager, db_manager)
                bot_thread = threading.Thread(target=app.bot.start_trading)
                bot_thread.start()
            flash('Trading bot started successfully!', 'success')
        elif bot_action == 'stop':
            if app.bot is not None:
                app.bot.stop_trading()
                app.bot = None
            flash('Trading bot stopped successfully!', 'success')

    return render_template('home.html')


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        api_key = request.form.get('api_key')
        api_secret = request.form.get('api_secret')
        paper = 'paper' in request.form

        if not api_key or not api_secret:
            flash('API Key and Secret are required!', 'error')
        else:
            app.config_manager.set_config('user_config', {'api_key': api_key, 'api_secret': api_secret, 'paper': paper})
            flash('Settings saved successfully!', 'success')

    user_config = app.config_manager.get_config('user_config')
    api_key = user_config.get('api_key') if user_config else None
    api_secret = user_config.get('api_secret') if user_config else None
    paper = user_config.get('paper') if user_config else None
    return render_template('settings.html', api_key=api_key, api_secret=api_secret, paper=paper)

@app.route('/strategy', methods=['GET', 'POST'])
def strategy():
    strategy_manager = StrategyManager(app.config_manager, db_manager)
    strategies = strategy_manager.get_all_strategies()
    active_strategy = db_manager.get_active_strategy()

    if request.method == 'POST':

        selected_strategy = request.form.get('strategy')

        if not selected_strategy:
            flash('Please select a valid strategy!', 'error')

        if not selected_strategy:
            flash('Please select a strategy!', 'error')
        else:
            db_manager.set_active_strategy(selected_strategy)
            flash('Active strategy set successfully!', 'success')
            active_strategy = selected_strategy

    return render_template('strategy.html', strategies=strategies, active_strategy=active_strategy)