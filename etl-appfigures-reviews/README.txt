# AppFigures Data Extraction and Upload

This script extracts review data from the AppFigures API, processes it, and uploads it to Google BigQuery. The process retrieves API credentials from Google Cloud Secret Manager, uses OAuth for authentication, and logs operations using Google Cloud Logging.

## Required Libraries

- `requests_oauthlib`
- `google.cloud.secretmanager`
- `pandas`
- `pandas_gbq`
- `flask`
- `google.cloud.logging`
- `google.cloud.bigquery`

## Environment Setup

- Google Cloud project with Secret Manager configured to store API credentials.
- Google Cloud Storage bucket for any interim storage needs.
- BigQuery dataset for storing the extracted data.
- Google Cloud Logging for logging operations.

## Functions

### `_get_secret(PROJECT_ID, name)`

Fetches secrets from Google Cloud Secret Manager.

- `PROJECT_ID`: Google Cloud Project ID.
- `name`: Name of the secret in Secret Manager.

### `_get_session(access_token=None)`

Handles OAuth session creation and authentication for the AppFigures API.

- `access_token`: Optional; an existing access token to use for the session.

### `appfigures_get_reviews(request)`

Main function that gets triggered by an HTTP request.

- Extracts parameters from a JSON payload in the HTTP request.
- Fetches the latest reviews from the AppFigures API.
- Processes the reviews and removes any redundant information.
- Uploads the processed data to a staging table in BigQuery.
- Merges the staging table with the main reviews table in BigQuery.

## Example Deployment

This script is designed to run as a Google Cloud Function triggered by HTTP requests. 

1. **Create a Google Cloud Function**:
    - Go to the [Google Cloud Console](https://console.cloud.google.com/).
    - Navigate to the Cloud Functions section.
    - Create a new function.

2. **Deploy the Function**:
    - Use the following command to deploy the function:

    ```sh
    gcloud functions deploy appfiguresGetReviews \
      --runtime python39 \
      --trigger-http \
      --entry-point appfigures_get_reviews \
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

This script provides a robust framework for extracting, processing, and storing review data from AppFigures. By leveraging Google Cloud services, it ensures scalability and reliability for ongoing data operations.