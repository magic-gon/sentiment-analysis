import google.cloud.bigquery as bigquery
import google.cloud.logging as gcp_logging

def run_query_load_all_obt(request):
    client = bigquery.Client()
    logger = gcp_logging.Client().logger("cloud-function-logger")

    if request.method == 'POST':
        request_json = request.get_json(silent=True)
        if not request_json:
            logger.log_text('Invalid or missing JSON payload', severity='ERROR')
            return 'Invalid or missing JSON payload', 400

        countries = request_json.get('countries')
        countries_merge = request_json.get('countries_merge')
        countries_short_replica = request_json.get('countries_short_replica')
        countries_short = request_json.get('countries_short')
        query = "CREATE OR REPLACE TABLE `some-project.some-dataset.some-table` AS (\nWITH"
        for country_merge, country, country_short_replica, country_short in zip(countries_merge, countries, countries_short_replica, countries_short):
            query += f"""
{country_merge} AS (
    SELECT
        "{country_merge}" AS country,
        t1.review,
        t1.id,
        t1.date,
        t1.store,
        t1.title,
        t1.stars,
        t1.version,
        t2.sentiment_magnitude,
        t2.sentiment_score,
        t3.payment_method,
        t3.add_credit,
        t3.wallet,
        t3.loyalty_points,
        t3.collect_points,
        t3.add_money,
        t3.customer_service,
        t3.app_upgrade,
        t3.load_money,
        t3.collect_stars,
        t3.app_update,
        t3.password_change,
        t3.password_reset,
        t4.payment,
        t4.login,
        t4.order,
        t4.scan,
        t4.reward,
        t4.registration
    FROM
        `client-{country.lower()}.some-dataset_{country_short_replica}.some-table_{country_short}_reviews` AS t1
    JOIN
        `client-{country.lower()}.some-dataset_{country_short_replica}.some-table_{country_short}_nlpapi_sentiment` AS t2
        ON t1.id = t2.id
    JOIN
        `client-{country.lower()}.some-dataset_{country_short_replica}.some-table_{country_short}_hf_needs` AS t3
        ON t1.id = t3.id
    JOIN
        `client-{country.lower()}.some-dataset_{country_short_replica}.some-table_{country_short}_hf_complaints` AS t4
        ON t1.id = t4.id
    ),\n
"""
        # Delete last coma and add the final query
        query = query[:-3]
        for country_merge in countries_merge:
            query += f"""
SELECT * FROM {country_merge}
UNION ALL
"""
        query = query[:-10]
        query += "\n)"
        
        try:
            query_job = client.query(query)
            results = query_job.result()
            logger.log_text(f"Query executed successfully", severity='INFO')
        except Exception as e:
            logger.log_text(f"Error executing query: {str(e)}", severity='ERROR')
            return f"Error executing query: {str(e)}", 500
        return f"Query executed successfully", 200
    else:
        return 'Method not allowed', 405