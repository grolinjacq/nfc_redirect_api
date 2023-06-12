from flask import Flask, request, redirect, render_template, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from config import config
from models import db, NFCTagCampaign, NFCCampaignLink, NFCLinkURL, NFCUser
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime
import os
import json
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError


# Create a Flask application
app = Flask(__name__)

# Set the secret key from the environment variable
app.secret_key = os.getenv('SECRET_KEY', 'default-secret-key')

# Load the application configuration
app.config.from_object(config)
db.init_app(app)

# Load BigQuery settings from the config
credentials = service_account.Credentials.from_service_account_info(json.loads(os.environ.get('BIGQUERY_CREDENTIALS')))
bigquery_client = bigquery.Client(credentials=credentials, project=config.BIGQUERY_PROJECT_ID)


###__LOGIN/REGISTRATION__###
############################

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# WTForms setup
class RegistrationForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired(), Length(max=100)])
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = NFCUser.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = NFCUser(username=form.username.data, company_name=form.company_name.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now registered, please login.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = NFCUser.query.filter_by(username=form.username.data).first()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password.')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@login_manager.user_loader
def load_user(user_id):
    return NFCUser.query.get(int(user_id))


###__METHODS__###
################


# Method for logging redirects on NFC tag redirect
def log_redirect(tag_id, campaign_id, link_id, link_url):
    table_id = f'{config.BIGQUERY_PROJECT_ID}.nfc_logs.nfc_redirect_log'

    # Prepare the data for insertion
    data = {
        'timestamp': datetime.utcnow(),
        'tag_id': tag_id,
        'campaign_id': campaign_id,
        'link_id': link_id,
        'link_url': link_url,
        'domain': request.host_url
    }

    # Insert the data into BigQuery
    table = bigquery_client.get_table(table_id)
    errors = bigquery_client.insert_rows(table, [data])

    if errors:
        # Handle any errors that occurred during insertion
        print(f'Error inserting row: {errors}')
    else:
        # Success message
        print('Row inserted successfully in redirect_log')



###__ROUTES__###
################


@app.route('/my_campaigns', methods=['GET', 'POST'])
@login_required
def my_campaigns():
    if request.method == 'POST':
        # Update the records in the database
        for link in NFCCampaignLink.query.filter_by(user_id=current_user.user_id).all():
            link_id = request.form.get('link_id_' + link.campaign_id)
            if link_id:
                link.link_id = link_id

        # Commit the changes for all records
        db.session.commit()

        # Flash a success message
        flash('Records updated successfully.', 'success')

        # Redirect to the 'my_campaigns' page
        return redirect(url_for('my_campaigns'))
    else:
        # Retrieve all 'NFCCampaignLink' records from the database for the current user
        my_campaigns = NFCCampaignLink.query.filter_by(user_id=current_user.user_id).all()

        # Render the 'my_campaigns.html' template with the retrieved records
        return render_template('my_campaigns.html', my_campaigns=my_campaigns)


@app.route('/my_tags', methods=['GET', 'POST'])
@login_required
def my_tags():
    if request.method == 'POST':
        # Update the campaign IDs in the database
        for tag in NFCTagCampaign.query.filter_by(user_id=current_user.user_id).all():
            campaign_id = request.form.get('campaign_id_' + tag.tag_id)
            if campaign_id:
                tag.campaign_id = campaign_id

        # Commit the changes for all records
        db.session.commit()

        # Flash a success message
        flash('Records updated successfully.', 'success')

        # Redirect to the 'my_tags' page
        return redirect(url_for('my_tags'))
    else:
        # Retrieve all 'NFCTagCampaign' records from the database for the current user
        my_tags = NFCTagCampaign.query.filter_by(user_id=current_user.user_id).all()

        # Render the 'my_tags.html' template with the retrieved records
        return render_template('my_tags.html', my_tags=my_tags)


@app.route('/my_links', methods=['GET', 'POST'])
@login_required
def my_links():
    if request.method == 'POST':
        # Update the records in the database
        for link in NFCLinkURL.query.filter_by(user_id=current_user.user_id).all():
            link_label = request.form.get('link_label_' + link.link_id)
            link_url = request.form.get('link_url_' + link.link_id)
            if link_label and link_url:
                link.link_label = link_label
                link.link_url = link_url

        # Commit the changes for all records
        db.session.commit()

        # Flash a success message
        flash('Records updated successfully.', 'success')

        # Redirect to the 'my_links' page
        return redirect(url_for('my_links'))
    else:
        # Retrieve all 'NFCLinkURL' records from the database for the current user
        my_links = NFCLinkURL.query.filter_by(user_id=current_user.user_id).all()

        # Render the 'my_links.html' template with the retrieved records
        return render_template('my_links.html', my_links=my_links)


# API endpoint to handle NFC tag redirection
@app.route('/redirect/<tag_id>')
def redirect_nfc(tag_id):
    tag = NFCTagCampaign.query.filter_by(tag_id=tag_id).first()

    if tag:
        campaign_link = NFCCampaignLink.query.filter_by(campaign_id=tag.campaign_id).first()

        if campaign_link:
            link_url = NFCLinkURL.query.filter_by(link_id=campaign_link.link_id).first()

            if link_url:
                log_redirect(tag_id, tag.campaign_id, campaign_link.link_id, link_url.link_url)
                return redirect(link_url.link_url)
            else:
                return 'Link URL not found.'
        else:
            return 'Campaign link not found.'
    else:
        return 'NFC tag not found.'


# Home route to display the index.html page
@app.route('/', methods=['GET', 'POST'])
@login_required
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
