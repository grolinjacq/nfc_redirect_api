import os
from google.cloud import secretmanager

# Get the absolute path to the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

class Config:
    # Set up the SQLite database path
    sqlite_db_path = os.path.join(current_dir, 'database', 'nfc_data.db')

    # Set the SQLite database URI if the DATABASE_URL environment variable is not set
    default_db_uri = f'sqlite:///{sqlite_db_path}'
    uri = os.environ.get('DATABASE_URL', default_db_uri)
    
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    # rest of connection code using the connection string `uri`
    
    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # BigQuery configuration
    BIGQUERY_PROJECT_ID = 'nfc-redirect-project'

    # Other configuration options for your Flask application
    # ...

# Create an instance of the Config class
config = Config()