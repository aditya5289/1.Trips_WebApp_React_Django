import os
import django
import requests
import pandas as pd
import logging
import time
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import connection, transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yellow_cab_project.settings')
django.setup()

from cabdata.models import YellowCab

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def disable_indexes(cursor):
    logger.info('Disabling indexes')
    cursor.execute('ALTER TABLE cabdata_yellowcab DISABLE KEYS')


def enable_indexes(cursor):
    logger.info('Enabling indexes')
    cursor.execute('ALTER TABLE cabdata_yellowcab ENABLE KEYS')


def import_data(file_path):
    logger.info(f'Starting to import data from {file_path}')
    start_time = time.time()

    data = pd.read_parquet(file_path)

    # Replace NaN values with appropriate defaults
    data.fillna({
        'VendorID': 0,
        'passenger_count': 0,
        'trip_distance': 0.0,
        'RatecodeID': 0,
        'store_and_fwd_flag': '',
        'PULocationID': 0,
        'DOLocationID': 0,
        'payment_type': 0,
        'fare_amount': 0.0,
        'extra': 0.0,
        'mta_tax': 0.0,
        'tip_amount': 0.0,
        'tolls_amount': 0.0,
        'improvement_surcharge': 0.0,
        'total_amount': 0.0,
        'congestion_surcharge': 0.0
    }, inplace=True)

    records = []

    for idx, row in data.iterrows():
        if idx % 10000 == 0:
            logger.info(f'Processing row {idx}/{len(data)}')

        record = YellowCab(
            VendorID=row['VendorID'],
            tpep_pickup_datetime=timezone.make_aware(row['tpep_pickup_datetime']),
            tpep_dropoff_datetime=timezone.make_aware(row['tpep_dropoff_datetime']),
            passenger_count=row['passenger_count'],
            trip_distance=row['trip_distance'],
            RatecodeID=row['RatecodeID'],
            store_and_fwd_flag=row['store_and_fwd_flag'],
            PULocationID=row['PULocationID'],
            DOLocationID=row['DOLocationID'],
            payment_type=row['payment_type'],
            fare_amount=row['fare_amount'],
            extra=row['extra'],
            mta_tax=row['mta_tax'],
            tip_amount=row['tip_amount'],
            tolls_amount=row['tolls_amount'],
            improvement_surcharge=row['improvement_surcharge'],
            total_amount=row['total_amount'],
            congestion_surcharge=row['congestion_surcharge']
        )
        records.append(record)

    # Using bulk_create for faster inserts
    batch_size = 10000  # Adjust batch size as needed
    with transaction.atomic():
        with connection.cursor() as cursor:
            disable_indexes(cursor)
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                YellowCab.objects.bulk_create(batch, batch_size=batch_size, ignore_conflicts=True)
                logger.info(f'Inserted batch {i // batch_size + 1}/{(len(records) - 1) // batch_size + 1}')
            enable_indexes(cursor)

    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f'Finished importing data. Total records imported: {len(records)}')
    logger.info(f'Time taken to import data: {elapsed_time} seconds')


def download_data(year, month):
    file_name = f"yellow_tripdata_{year}-{month:02d}.parquet"
    url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{file_name}"
    logger.info(f'Downloading data for {year}-{month:02d} from {url}')
    response = requests.get(url)
    with open(file_name, 'wb') as file:
        file.write(response.content)
    logger.info(f'Download completed and saved to {file_name}')
    return file_name


def manage_data(year, month):
    logger.info(f'Checking if data for {year}-{month:02d} is already in the database')
    if not YellowCab.objects.filter(tpep_pickup_datetime__year=year, tpep_pickup_datetime__month=month).exists():
        logger.info(f'Data for {year}-{month:02d} not found in the database. Initiating download and import.')
        file_path = download_data(year, month)
        import_data(file_path)

        logger.info(f'Ensuring no more than 3 months of data are kept')
        # Get distinct months currently in the database
        months_in_db = YellowCab.objects.dates('tpep_pickup_datetime', 'month', order='ASC')
        if len(months_in_db) > 3:
            # Find the oldest month to delete
            oldest_month = months_in_db[0]
            delete_count, _ = YellowCab.objects.filter(tpep_pickup_datetime__year=oldest_month.year,
                                                       tpep_pickup_datetime__month=oldest_month.month).delete()
            logger.info(f'Deleted {delete_count} records from the oldest month: {oldest_month}')
    else:
        logger.info(f'Data for {year}-{month:02d} is already present in the database. No action needed.')


if __name__ == '__main__':
    year = 2024
    month = 1
    logger.info(f'Starting data management for {year}-{month:02d}')
    manage_data(year, month)
    logger.info(f'Data management for {year}-{month:02d} completed')
