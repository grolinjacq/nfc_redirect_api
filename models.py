from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

# Define the User model
class NFCUser(UserMixin, db.Model):
    __tablename__ = 'nfc_users'
    user_id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.user_id)

# Define the NFC tag model
class NFCTagCampaign(db.Model):
    __tablename__ = 'nfc_tag_campaign'
    tag_id = db.Column(db.String(50), primary_key=True)
    campaign_id = db.Column(db.String(50), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('nfc_users.user_id'))

    def __repr__(self):
        return f'<NFCTagCampaign {self.tag_id}>'

# Define the NFC campaign link model
class NFCCampaignLink(db.Model):
    __tablename__ = 'nfc_campaign_link'
    campaign_id = db.Column(db.String(50), primary_key=True)
    link_id = db.Column(db.String(50), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('nfc_users.user_id'))

    def __repr__(self):
        return f'<NFCCampaignLink {self.campaign_id}>'

# Define the NFC link URL model
class NFCLinkURL(db.Model):
    __tablename__ = 'nfc_link_url'
    link_id = db.Column(db.String(50), primary_key=True)
    link_label = db.Column(db.String(50))
    link_url = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('nfc_users.user_id'))

    def __repr__(self):
        return f'<NFCLinkURL {self.link_id}>'

# Defines a model for the log table, specifying the columns for id, timestamp, tag_id, campaign_id, link_id, and link_url.
class NFCRedirectLog(db.Model):
    __tablename__ = 'nfc_redirect_log'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, primary_key=True)
    tag_id = db.Column(db.String(255))
    campaign_id = db.Column(db.String(255))
    link_id = db.Column(db.String(255))
    link_url = db.Column(db.String(255))
    domain = db.Column(db.String(255))

