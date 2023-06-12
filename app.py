from flask import Flask, request, redirect, render_template, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from config import config
from models import db, NFCTagCampaign, NFCCampaignLink, NFCLinkURL, NFCUser
import os


# Create a Flask application
app = Flask(__name__)

# Set the secret key from the environment variable
app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key')

# Load the application configuration
app.config.from_object(config)
db.init_app(app)


###_API_ENDPOINTS_###
#####################

# API endpoint to handle NFC tag redirection
@app.route('/redirect/<tag_id>')
def redirect_nfc(tag_id):
    tag = NFCTagCampaign.query.filter_by(tag_id=tag_id).first()

    if tag:
        campaign_link = NFCCampaignLink.query.filter_by(campaign_id=tag.campaign_id).first()

        if campaign_link:
            link_url = NFCLinkURL.query.filter_by(link_id=campaign_link.link_id).first()

            if link_url:
                return redirect(link_url.link_url)
            else:
                return 'Link URL not found.'
        else:
            return 'Campaign link not found.'
    else:
        return 'NFC tag not found.'


# Home route to display the index.html page
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        nfc_id = request.form['nfc_id']
        return redirect(url_for('redirect_nfc', tag_id=nfc_id))
    else:
        # Get the current database URI
        current_database = app.config['SQLALCHEMY_DATABASE_URI']
        
        # Render the 'index.html' template with the current database passed
        return render_template('index.html', current_database=current_database)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
