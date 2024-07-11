# Sentiment Analysis and BigQuery Merge

This script performs sentiment analysis on text data from a BigQuery table and merges the results back into another BigQuery table. The sentiment analysis is performed using Google Cloud Natural Language API, and Google Cloud Logging is used for logging operations.

## Required Libraries

- `google-cloud-bigquery`
- `flask`
- `google-cloud-language`
- `google-cloud-logging`
- `pandas`
- `pandas_gbq`

## Environment Setup

- Google Cloud project with access to BigQuery and Google Cloud Natural Language API.
- BigQuery dataset to store the sentiment analysis results.
- Google Cloud Logging for logging operations.

## Functions

### `analyze_sentiment_and_merge(request)`

Main function that gets triggered by an HTTP request.

- Extracts parameters from a JSON payload in the HTTP request.
- Performs sentiment analysis on text data.
- Uploads the sentiment analysis results to a staging table in BigQuery.
- Merges the staging table with the main sentiment table in BigQuery.

## Example Deployment

This script is designed to run as a Google Cloud Function triggered by HTTP requests.

1. **Create a Google Cloud Function**:
    - Go to the [Google Cloud Console](https://console.cloud.google.com/).
    - Navigate to the Cloud Functions section.
    - Create a new function.

2. **Deploy the Function**:
    - Use the following command to deploy the function:

    ```sh
    gcloud functions deploy sentimentAnalysisAndMerge \
      --runtime python39 \
      --trigger-http \
      --entry-point analyze_sentiment_and_merge \
      --env-vars-file .env.yaml
    ```

### .env.yaml

Ensure you have an `.env.yaml` file with necessary environment variables for authentication and configuration.

## Logging

All operations and errors are logged using Google Cloud Logging. To view the logs:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Navigate to the Logging section.
3. View logs for the specific function to monitor its operations and troubleshoot any issues.

## Conclusion

This script provides a robust framework for performing sentiment analysis on text data and merging the results back into BigQuery. By leveraging Google Cloud services, it ensures scalability and reliability for ongoing data operations.