from requests_oauthlib import OAuth2Session
from google.cloud import secretmanager
import pandas as pd
import pandas_gbq
import json
from flask import escape
from datetime import datetime, timedelta
from google.cloud import logging as gcp_logging
from google.cloud import bigquery

# Configure GCP logging
logger = gcp_logging.Client().logger(__name__)


# Function to get secrets from Secret Manager
def _get_secret(PROJECT_ID,name):
    secret_client = secretmanager.SecretManagerServiceClient()
    secret_name = f'projects/{PROJECT_ID}/secrets/{name}/versions/latest'
    response=secret_client.access_secret_version(request={'name':secret_name})
    return response

# Get secrets
CLIENT_KEY = _get_secret(PROJECT_ID='some-id',name='some-name').payload.data.decode('UTF-8')
CLIENT_SECRET = _get_secret(PROJECT_ID='some-id',name='some-name-2').payload.data.decode('UTF-8')
PAT = _get_secret(PROJECT_ID='some-id',name='some-name-3').payload.data.decode('UTF-8')

# Define URLs
BASE_URL = "https://api.appfigures.com/v2"
AUTHORIZE_URL = BASE_URL + "/oauth2/authorize"
ACCESS_TOKEN_URL = BASE_URL + "/oauth2/access_token"
SCOPES = ["account:read", "products:read", "public:read", "private:read"]

# AppFigures API Auth Function
def _get_session(access_token=None):
    """If access_token and secret are given, create and return a session.

    If they are not given, go through the authorization process
    interactively and return the new session
    """
    session = OAuth2Session(client_id=CLIENT_KEY, scope=SCOPES, redirect_uri="oob")
    if access_token:
        session.token = {"access_token": access_token, "token_type": "bearer"}
        return session

    authorization_url, state = session.authorization_url(AUTHORIZE_URL)
    print("Please go here and authorize: %s" % authorization_url)
    code = input("Paste the code you were given here:")
    token = session.fetch_token(
        ACCESS_TOKEN_URL,
        client_secret=CLIENT_SECRET,
        code=access_token,
        auth=(CLIENT_KEY, CLIENT_SECRET),
    )
    return session

def appfigures_get_reviews(request):
    # Get parameters from Workflows
    if request.method == 'POST':
        request_json = request.get_json(silent=True)
        
        # If there is no JSON in the request or it's empty, return an error
        if not request_json:
            return 'Invalid or missing JSON payload', 400

        # Extract parameters directly from JSON
        PROJECT_ID = request_json.get('project_id')
        DATASET_ID = request_json.get('dataset_id')
        REVIEWS_TABLE_ID = request_json.get('reviews_table_id')
        PRODUCTS = request_json.get('products')
    # Run the user through the authorization process!
    s = _get_session(access_token=PAT)
    logger.log_struct(
                {
                    'message': 'Starting review retrieval process.'
                },
                severity='INFO'
            )
    # Get the latest date from the table to reduce the request. 
    latest_date_query = f"""
    SELECT MAX(date) as max_date FROM `{PROJECT_ID}.{DATASET_ID}.{REVIEWS_TABLE_ID}`
    """
    try:
        latest_date_df = pandas_gbq.read_gbq(latest_date_query, project_id=PROJECT_ID)
        latest_date_str = latest_date_df.loc[0, 'max_date']
        
        if pd.isnull(latest_date_str):  # Use pd.isnull to check for None or NaN values
            # Log that no new start date will be used as MAX(date) returned None
            logger.log_struct(
                {
                    'message': 'MAX(date) returned None, omitting start parameter.',
                },
                severity='INFO'
            )
            start_date_str = None  # Remove the start parameter if None was returned
        else:
            # Update the format to include time component
            latest_date = datetime.strptime(latest_date_str, '%Y-%m-%dT%H:%M:%S').date()
            start_date = latest_date - timedelta(days=1)
            start_date_str = start_date.strftime('%Y-%m-%d')

    except Exception as e:
        logger.log_struct(
            {
                'message': f"Error getting latest date: {str(e)}",
                'exception_type': type(e).__name__  # Including the exception type in the log
            },
            severity='WARNING'
        )
        latest_date = datetime.now().date() - timedelta(days=1)  # If there's an error, use yesterday's date as a fallback
        start_date_str = latest_date.strftime('%Y-%m-%d')
    
    page = 1
    total_reviews = []
    processed_pages = 0  # Initialize a counter for processed pages

    try:
        while True:
            # Fetch reviews with or without start date as needed, construct the request URL accordingly
            params = {"products": PRODUCTS, "page": page}
            if start_date_str:  # If there's a start date, add it to the parameters
                params["start"] = start_date_str
            resp = s.get(BASE_URL + "/reviews", params=params)
            
            # Check response status and exit loop if something goes wrong or no more data is available
            if resp.status_code != 200 or not resp.json().get("reviews"):
                break

            reviews = resp.json()["reviews"]
            if not reviews:  # Exit the loop if there are no more reviews
                break

            total_reviews.extend(reviews)
            processed_pages += 1  # Increment the processed page count
            page += 1
    
    except Exception as e:
        logger.log_struct(
            {
                'message': f"Error occurred: {str(e)}"
            },
            severity='WARNING'
        )
    
    logger.log_struct(
    {
        'message': f"Total pages processed: {processed_pages}"
    },
    severity='INFO'
)
    
    fields = [
        {
            'id': record.get('id'),
            'title': record.get('title'),
            'review': record.get('review'),
            'original_title': record.get('original_title'),
            'stars': record.get('stars'),
            'iso': record.get('iso'),
            'version': record.get('version'),
            'date': record.get('date'),
            'deleted': record.get('deleted'),
            'has_response': record.get('has_response'),
            'product': record.get('product'),
            'product_id': record.get('product_id'),
            'store': record.get('store'),
            
        }
        for record in total_reviews
    ]
    
    #   Create the dataframe
    df = pd.DataFrame(fields)
    staging_table_id = f"{PROJECT_ID}.{DATASET_ID}.staging_{REVIEWS_TABLE_ID}"

    try:
        pandas_gbq.to_gbq(df, staging_table_id, project_id=PROJECT_ID, if_exists='replace')
        logger.log_struct(
            {
                'message': f"Data uploaded to BigQuery staging table: {staging_table_id}"
            },
            severity='INFO'
        )
    except Exception as e:
        logger.log_struct(
            {
                'message': f"Error occurred during staging data upload: {str(e)}"
            },
            severity='WARNING'
        )
    
    # Merge update based on id
    merge_query = f"""
        MERGE `{PROJECT_ID}.{DATASET_ID}.{REVIEWS_TABLE_ID}` AS target
        USING `{staging_table_id}` AS source
        ON target.id = source.id
        WHEN MATCHED THEN
            UPDATE SET
                target.title = source.title,
                target.review = source.review,
                target.original_title = source.original_title,
                target.stars = source.stars,
                target.iso = source.iso,
                target.version = source.version,
                target.date = source.date,
                target.deleted = source.deleted,
                target.has_response = source.has_response,
                target.product = source.product,
                target.product_id = source.product_id,
                target.store = source.store
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (id, title, review, original_title, stars, iso, version, date, deleted, has_response, product, product_id, store)
            VALUES (source.id, source.title, source.review, source.original_title, source.stars, source.iso, source.version, source.date, source.deleted, source.has_response, source.product, source.product_id, source.store)
    """
    try:
        client = bigquery.Client(project=PROJECT_ID)
        job = client.query(merge_query)
        job.result()
        logger.log_struct(
            {
                'message': f"Merge operation completed successfully."
            },
            severity='INFO'
        )

    except Exception as e:
        logger.log_struct(
            {
                'message': f"Error occurred during merge update: {str(e)}"
            },
            severity='WARNING'
        )
    return 'Function executed successfully', 200