from flask import Flask, render_template, request, flash, redirect, url_for
from database_manager.database_manager import DatabaseManager

# Create the Flask app instance
app = Flask(__name__)
app.secret_key = 'unpredictablekey'  # This should be a secure, unpredictable key
# Create the db_manager instance inside the app context
with app.app_context():
    app.db_manager = DatabaseManager()


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        bot_status = 'bot_status' in request.form
        api_key, api_secret, _ = app.db_manager.retrieve_user_config()
        if not api_key or not api_secret:
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
            app.db_manager.store_user_config(api_key, api_secret, paper)
            flash('Settings saved successfully!', 'success')

    api_key, api_secret, paper = app.db_manager.retrieve_user_config()
    return render_template('settings.html', api_key=api_key, api_secret=api_secret, paper=paper)


@app.route('/strategy_selection')
def strategy_selection():
    return render_template('strategy_selection.html')


@app.route('/strategy_purchase', methods=['GET', 'POST'])
def strategy_purchase():
    if request.method == 'POST':
        # TODO: Add Stripe integration here to handle purchase
        flash('Strategy purchase successful!', 'success')

    return render_template('strategy_purchase.html')

# if __name__ == '__main__':
#     app.run(debug=True)
