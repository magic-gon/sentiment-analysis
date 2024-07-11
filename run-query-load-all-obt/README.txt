# BigQuery Table Creation and Data Loading

This script creates or replaces a BigQuery table by merging data from multiple sources based on a list of countries. It uses Google Cloud Logging for monitoring and BigQuery for data manipulation.

## Required Libraries

- `google-cloud-bigquery`
- `google-cloud-logging`

## Environment Setup

- Google Cloud project with access to BigQuery and Google Cloud Logging.
- BigQuery datasets and tables as specified in the script.

## Functions

### `run_query_load_all_obt(request)`

Main function that gets triggered by an HTTP request.

- Extracts parameters from a JSON payload in the HTTP request.
- Constructs a BigQuery SQL query to merge data from multiple sources.
- Executes the constructed SQL query.
- Logs operations and errors using Google Cloud Logging.

## Example Deployment

This script is designed to run as a Google Cloud Function triggered by HTTP requests.

1. **Create a Google Cloud Function**:
    - Go to the [Google Cloud Console](https://console.cloud.google.com/).
    - Navigate to the Cloud Functions section.
    - Create a new function.

2. **Deploy the Function**:
    - Use the following command to deploy the function:

    ```sh
    gcloud functions deploy runQueryLoadAllObt \
      --runtime python39 \
      --trigger-http \
      --entry-point run_query_load_all_obt \
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

This script provides a robust framework for creating and loading BigQuery tables by merging data from multiple sources. By leveraging Google Cloud services, it ensures scalability and reliability for ongoing data operations.