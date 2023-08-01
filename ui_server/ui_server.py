from flask import Flask, render_template, request, flash, redirect, url_for
from database_manager.database_manager import DatabaseManager
from configuration_manager.configuration_manager import ConfigurationManager

# Create the Flask app instance
app = Flask(__name__)
app.secret_key = 'unpredictablekey'  # This should be a secure, unpredictable key

# Create the db_manager instance inside the app context
with app.app_context():
    db_manager = DatabaseManager()
    app.config_manager = ConfigurationManager(db_manager)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        bot_status = 'bot_status' in request.form
        user_config = app.config_manager.get_config('user_config')
        if not user_config or not user_config.get('api_key') or not user_config.get('api_secret'):
            flash('API Key and Secret are required!', 'error')
            return redirect(url_for('settings'))
        flash('Trading bot status updated successfully!', 'success')

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


# @app.route('/strategy_selection')
# def strategy_selection():
#     return render_template('strategy_selection.html')
#
#
# @app.route('/strategy_purchase', methods=['GET', 'POST'])
# def strategy_purchase():
#     if request.method == 'POST':
#         # TODO: Add Stripe integration here to handle purchase
#         flash('Strategy purchase successful!', 'success')
#
#     return render_template('strategy_purchase.html')
