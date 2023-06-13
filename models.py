from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Define the NFC tags model
class NFCTags(db.Model):
    __tablename__ = 'nfc_tags'
    tag_id = db.Column(db.String(50), primary_key=True)
    tag_camp_id = db.Column(db.String(50), nullable=False)
    tag_batch_id = db.Column(db.String(50), nullable=False)
    tag_batch_label = db.Column(db.String(100))
    tag_creation_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<NFCTagCampaign {self.tag_id}>'

# Define the NFC campaigns model
class NFCCampaigns(db.Model):
    __tablename__ = 'nfc_campaigns'
    camp_id = db.Column(db.String(50), primary_key=True)
    camp_link_id = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<NFCCampaignLink {self.camp_id}>'

# Define the NFC links model
class NFCLinks(db.Model):
    __tablename__ = 'nfc_links'
    link_id = db.Column(db.String(50), primary_key=True)
    link_label = db.Column(db.String(50))
    link_url = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<NFCLinkURL {self.link_id}>'

# Define the NFC Batches model
class NFCBatches(db.Model):
    __tablename__ = 'nfc_batches'
    batch_id = db.Column(db.String(50), primary_key=True)
    batch_label = db.Column(db.String(100), nullable=False)
    batch_num_tags = db.Column(db.Integer, nullable=False)
    batch_camp_id = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<NFCBatch {self.batch_id}>'

