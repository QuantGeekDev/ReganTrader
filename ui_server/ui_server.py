# ui_server.py
from flask import Flask, render_template, request, flash, redirect, url_for
import threading
from bot_service.bot_service import BotService

app = Flask(__name__)
app.secret_key = 'unpredictablekey'  # This should be a secure, unpredictable key
service = BotService()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        bot_action = request.form.get('bot_action')
        user_config = service.get_settings()
        if not user_config or not user_config.get('api_key') or not user_config.get('api_secret'):
            flash('API Key and Secret are required!', 'error')
            return redirect(url_for('settings'))
        if bot_action == 'start':
            service.start_bot()
            flash('Trading bot started successfully!', 'success')
        elif bot_action == 'stop':
            service.stop_bot()
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
            service.update_settings({'api_key': api_key, 'api_secret': api_secret, 'paper': paper})
            flash('Settings saved successfully!', 'success')

    user_config = service.get_settings()
    api_key = user_config.get('api_key') if user_config else None
    api_secret = user_config.get('api_secret') if user_config else None
    paper = user_config.get('paper') if user_config else None
    return render_template('settings.html', api_key=api_key, api_secret=api_secret, paper=paper)

@app.route('/strategy', methods=['GET', 'POST'])
def strategy():
    strategies = service.get_all_strategies()
    active_strategy = service.get_active_strategy()

    if request.method == 'POST':
        selected_strategy = request.form.get('strategy')

        if not selected_strategy:
            flash('Please select a strategy!', 'error')
        else:
            service.set_active_strategy(selected_strategy)
            flash('Active strategy set successfully!', 'success')
            active_strategy = selected_strategy

    return render_template('strategy.html', strategies=strategies, active_strategy=active_strategy)
