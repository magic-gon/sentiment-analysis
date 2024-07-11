# Zero-Shot Classification and BigQuery Merge

This script uses FastAPI to create an endpoint that performs zero-shot classification on text data from a BigQuery table and merges the results back into another BigQuery table. The zero-shot classification model is loaded using the `transformers` library. The process also leverages Google Cloud Logging for monitoring and pandas for data manipulation.

## Required Libraries

- `fastapi`
- `pydantic`
- `typing`
- `google-cloud-bigquery`
- `google-cloud-logging`
- `pandas`
- `pandas_gbq`
- `os`
- `transformers`
- `asyncio`
- `uvicorn`
- `concurrent.futures`
- `functools`
- `time`

## Environment Setup

- Google Cloud project with access to BigQuery and Google Cloud Logging.
- BigQuery dataset to store the classification results.
- Google Cloud Logging for monitoring operations.

## FastAPI Pydantic Model

### `AnalyzeRequest`

Defines the expected structure for the request body when calling the `/analyze` endpoint:

- `project_id`: Google Cloud Project ID.
- `dataset_id`: BigQuery Dataset ID.
- `reviews_table_id`: BigQuery Table ID containing the reviews.
- `topic_table_id`: BigQuery Table ID to store the classification results.
- `topics`: List of topics for zero-shot classification.
- `isoweek`: Optional; ISO Week number for filtering reviews.
- `day`: Optional; Specific day for filtering reviews in YYYY-MM-DD format.

## Functions

### `analyze_sentiment_and_merge(request_data: AnalyzeRequest)`

Main function that gets triggered by a POST request to the `/analyze` endpoint.

- Extracts parameters from the request body.
- Queries the BigQuery table for reviews.
- Performs zero-shot classification on the reviews.
- Uploads the classification results to a staging table in BigQuery.
- Merges the staging table with the main topic table in BigQuery.

### `process_row(row, topics)`

Processes a single row for classification.

- `row`: Tuple containing row data.
- `topics`: List of topics for zero-shot classification.

### `process_rows_with_multiprocessing(query_results, topics)`

Uses multiprocessing to process multiple rows in parallel.

- `query_results`: List of tuples containing row data.
- `topics`: List of topics for zero-shot classification.

### `query_and_classify(request_data: AnalyzeRequest)`

Queries the BigQuery table and classifies the reviews.

- `request_data`: Instance of `AnalyzeRequest` containing request parameters.

### `upload_to_bigquery(results, staging_table_id, project_id, logger)`

Uploads the classification results to a staging table in BigQuery.

- `results`: List of classification results.
- `staging_table_id`: BigQuery Table ID for staging.
- `project_id`: Google Cloud Project ID.
- `logger`: Instance of Google Cloud Logger.

### `merge_data(project_id, dataset_id, topic_table_id, staging_table_id, unique_labels, logger)`

Merges the staging table with the main topic table in BigQuery.

- `project_id`: Google Cloud Project ID.
- `dataset_id`: BigQuery Dataset ID.
- `topic_table_id`: BigQuery Table ID for topics.
- `staging_table_id`: BigQuery Table ID for staging.
- `unique_labels`: Set of unique labels (topics).
- `logger`: Instance of Google Cloud Logger.

## Example Deployment

This script is designed to be deployed on Google Cloud Run.

1. **Build the Docker Image**:
    ```sh
    docker build -t gcr.io/PROJECT-ID/your-image-name .
    ```

2. **Push the Docker Image to Google Container Registry**:
    ```sh
    docker push gcr.io/PROJECT-ID/your-image-name
    ```

3. **Deploy the Image to Google Cloud Run**:
    ```sh
    gcloud run deploy your-service-name --image gcr.io/PROJECT-ID/your-image-name --platform managed
    ```

Replace `PROJECT-ID` with your Google Cloud project ID and `your-image-name` with your Docker image name.

## Logging

All operations and errors are logged using Google Cloud Logging. To view the logs:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Navigate to the Logging section.
3. View logs for the specific service to monitor its operations and troubleshoot any issues.

## Conclusion

This script provides a robust framework for performing zero-shot classification on text data and merging the results back into BigQuery. By leveraging FastAPI, Google Cloud, and the `transformers` library, it ensures scalability, reliability, and fast data processing for ongoing data operations.