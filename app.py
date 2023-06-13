from flask import Flask, request, redirect, render_template, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from config import config
from models import db, NFCTags, NFCCampaigns, NFCLinks, NFCBatches
import os
import shortuuid
from datetime import datetime



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
@app.route('/api/redirect/<tag_id>')
def redirect_nfc(tag_id):
    tag = NFCTags.query.filter_by(tag_id=tag_id).first()

    if tag:
        camp_id = NFCCampaigns.query.filter_by(camp_id=tag.tag_camp_id).first()

        if camp_id:
            link_url = NFCLinks.query.filter_by(link_id=camp_id.camp_link_id).first()

            if link_url:
                return redirect(link_url.link_url)
            else:
                return 'Link URL not found.'
        else:
            return 'Campaign link not found.'
    else:
        return 'NFC tag not found.'


# API endpoint to handle NFC tags creation via Batch creation
def generate_unique_id():
    return shortuuid.uuid()

@app.route('/api/create_batch', methods=['POST'])
def create_batch():
    if request.method == 'POST':
        data = request.get_json()
        num_tags = data['num_tags']

        # Check if number of tags exceeds the limit
        if num_tags > 10:
            return {'message': 'Exceeded maximum limit of 10 tags per batch'}, 400

        batch_id = generate_unique_id()
        for i in range(data['num_tags']):
            new_tag = NFCTags(
                tag_id=f"{batch_id}-{i}",  # Here, we append the unique number in the batch to the tag's ID
                tag_camp_id=data['camp_id'],
                tag_batch_id=batch_id,
                tag_batch_label=data['batch_label'],
                tag_creation_date=datetime.utcnow()
            )
            db.session.add(new_tag)
        
        new_batch = NFCBatches(
            batch_id=batch_id,
            batch_label=data['batch_label'],
            batch_num_tags=data['num_tags'],
            batch_camp_id=data['camp_id']
        )
        db.session.add(new_batch)

        db.session.commit()

        return {'message': 'Batch created successfully'}, 201

    return {'message': 'Method not allowed'}, 405




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
