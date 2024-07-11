from google.cloud import bigquery
from flask import escape
from google.cloud import language_v1
from google.cloud import logging as gcp_logging
import pandas as pd
import pandas_gbq
import os

def analyze_sentiment_and_merge(request):
    logger = gcp_logging.Client().logger("cloud-function-logger")

    if request.method == 'POST':
        request_json = request.get_json(silent=True)
        if not request_json:
            logger.log_text('Invalid or missing JSON payload', severity='ERROR')
            return 'Invalid or missing JSON payload', 400

        PROJECT_ID = request_json.get('project_id')
        DATASET_ID = request_json.get('dataset_id')
        REVIEWS_TABLE_ID = request_json.get('reviews_table_id')
        SENTIMENT_TABLE_ID = request_json.get('sentiment_table_id')
        source_table = f'`{PROJECT_ID}.{DATASET_ID}.{REVIEWS_TABLE_ID}`'
        destination_table = f'{PROJECT_ID}.{DATASET_ID}.{SENTIMENT_TABLE_ID}'

    client = bigquery.Client(project=PROJECT_ID)
    language_client = language_v1.LanguageServiceClient()

    query = f"""
    SELECT s.*
    FROM {source_table} AS s
    LEFT JOIN {destination_table} AS d ON s.id = d.id
    WHERE d.id IS NULL;
    """

    query_job = client.query(query)

    results = query_job.result()

    rows = []
    for row in results:
        try:
            id = row.id
            review = row.review
            document = language_v1.Document(content=review, type_=language_v1.Document.Type.PLAIN_TEXT)
            sentiment = language_client.analyze_sentiment(request={'document': document}).document_sentiment
            sentiment_score = sentiment.score
            sentiment_magnitude = sentiment.magnitude
            rows.append((id, sentiment_score, sentiment_magnitude))
        except Exception as e:
            logger.log_text(f'Error processing row: {row}, Error: {e}', severity='WARNING')

    df = pd.DataFrame(rows, columns=['id', 'sentiment_score', 'sentiment_magnitude'])
    staging_table_id = f"{PROJECT_ID}.{DATASET_ID}.staging_{SENTIMENT_TABLE_ID}"

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
        MERGE `{PROJECT_ID}.{DATASET_ID}.{SENTIMENT_TABLE_ID}` AS target
        USING `{staging_table_id}` AS source
        ON target.id = source.id
        WHEN MATCHED THEN
            UPDATE SET
                target.sentiment_score = source.sentiment_score,
                target.sentiment_magnitude = source.sentiment_magnitude
        WHEN NOT MATCHED BY TARGET THEN
            INSERT (id, sentiment_score, sentiment_magnitude)
            VALUES (source.id, source.sentiment_score, source.sentiment_magnitude)
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