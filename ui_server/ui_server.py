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
        if not service.get_connection_setting('api_key') or not service.get_connection_setting('api_secret'):
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
            service.set_connection_setting('api_key', api_key)
            service.set_connection_setting('api_secret', api_secret)
            service.set_connection_setting('paper', paper)
            flash('Settings saved successfully!', 'success')

    api_key = service.get_connection_setting('api_key')
    api_secret = service.get_connection_setting('api_secret')
    paper = service.get_connection_setting('paper')
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
