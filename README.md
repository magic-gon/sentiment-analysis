# Data ETL Pipeline

This repository contains scripts for extracting data from various APIs, processing it to remove Personally Identifiable Information (PII), performing sentiment analysis, performing zero-shot classification, and storing the results in Google Cloud services before loading them into BigQuery. The process is automated using Google Cloud Functions, Google Cloud Run, and Pub/Sub to manage and trigger data flows.

## Overview

The ETL pipeline consists of several main scripts:

### AppFigures ETL Scripts

1. **appfigures_data_extraction.py**:
    - Extracts review data from the AppFigures API.
    - Uses Google Cloud Secret Manager to manage API credentials.
    - Processes and uploads the data to a staging table in BigQuery.
    - Merges the staging table with the main reviews table in BigQuery.

### Google Cloud Natural Language ETL Scripts

2. **sentiment_analysis_and_merge.py**:
    - Performs sentiment analysis on text data from a BigQuery table.
    - Uploads the sentiment analysis results to a staging table in BigQuery.
    - Merges the staging table with the main sentiment table in BigQuery.

### Zero-Shot Classification ETL Scripts

3. **zero_shot_classification.py**:
    - Uses FastAPI to create an endpoint for zero-shot classification on text data from a BigQuery table.
    - Performs zero-shot classification using a model from the `transformers` library.
    - Uploads the classification results to a staging table in BigQuery.
    - Merges the staging table with the main topic table in BigQuery.

### BigQuery Table Creation and Data Loading

4. **run_query_load_all_obt.py**:
    - Creates or replaces a BigQuery table by merging data from multiple sources based on a list of countries.
    - Uses Google Cloud Logging for monitoring and BigQuery for data manipulation.
    - Logs operations and errors using Google Cloud Logging.

## Detailed Description of Each Script

### appfigures_data_extraction.py

- **Purpose**: Extract review data from the AppFigures API, process it and upload it to BigQuery.
- **Functions**:
  - `_get_secret(PROJECT_ID, name)`: Retrieves API credentials from Secret Manager.
  - `_get_session(access_token=None)`: Manages OAuth authentication for the AppFigures API.
  - `appfigures_get_reviews(request)`: Main function to extract and process reviews and load them into BigQuery.
- **Usage**: Deploy as a Google Cloud Function triggered by HTTP requests.

### sentiment_analysis_and_merge.py

- **Purpose**: Perform sentiment analysis on text data from a BigQuery table and upload the results to BigQuery.
- **Functions**:
  - `analyze_sentiment_and_merge(request)`: Main function to perform sentiment analysis, upload results to a staging table, and merge with the main sentiment analysis table.
- **Usage**: Deploy as a Google Cloud Function triggered by HTTP requests.

### zero_shot_classification.py

- **Purpose**: Perform zero-shot classification on text data from a BigQuery table and upload the results to BigQuery.
- **Functions**:
  - `analyze_sentiment_and_merge(request_data: AnalyzeRequest)`: Main function to extract text data from BigQuery, perform zero-shot classification, upload results to a staging table, and merge with the main topic table in BigQuery.
  - `process_row(row, topics)`: Processes a single row for classification.
  - `process_rows_with_multiprocessing(query_results, topics)`: Uses multiprocessing to process multiple rows in parallel.
  - `query_and_classify(request_data: AnalyzeRequest)`: Queries the BigQuery table and classifies the text data.
  - `upload_to_bigquery(results, staging_table_id, project_id, logger)`: Uploads the classification results to a staging table in BigQuery.
  - `merge_data(project_id, dataset_id, topic_table_id, staging_table_id, unique_labels, logger)`: Merges the staging table with the main topic table in BigQuery.
- **Usage**: Deploy as a service on Google Cloud Run.

### run_query_load_all_obt.py

- **Purpose**: Creates or replaces a BigQuery table by merging data from multiple sources based on a list of countries.
- **Functions**:
  - `run_query_load_all_obt(request)`: Main function to create or replace a BigQuery table by merging data from multiple sources.
- **Usage**: Deploy as a Google Cloud Function triggered by HTTP requests.

## Deployment

Each script can be deployed as an individual service in Google Cloud. Ensure you have the necessary Google Cloud resources (Pub/Sub topics, GCS buckets, BigQuery datasets).

Example deployment commands:

### Google Cloud Functions

```sh
gcloud functions deploy FUNCTION_NAME \
  --runtime python39 \
  --trigger-RESOURCE_TYPE \
  --entry-point FUNCTION_ENTRY_POINT \
  --env-vars-file .env.yaml