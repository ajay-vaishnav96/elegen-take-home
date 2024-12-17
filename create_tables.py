import boto3
import os

from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Ensure AWS credentials and configurations are in place
try:
    # Dynamically configure credentials (if needed)
    boto3.setup_default_session(
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name="us-west-2"
    )
except (NoCredentialsError, PartialCredentialsError) as e:
    app.logger.error("AWS credentials not configured properly: %s", e)
    raise

# DynamoDB setup
dynamodb = boto3.resource("dynamodb", region_name="us-west-2")

def create_samples_table():
    table_name = "Samples"
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "sample_uuid", "KeyType": "HASH"}  # Partition key
            ],
            AttributeDefinitions=[
                {"AttributeName": "sample_uuid", "AttributeType": "S"}
            ],
            ProvisionedThroughput={
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            }
        )
        table.wait_until_exists()
        print(f"Table {table_name} created successfully.")
    except Exception as e:
        print(f"Error creating table {table_name}: {e}")

def create_orders_table():
    table_name = "Orders"
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "order_uuid", "KeyType": "HASH"}  # Partition key
            ],
            AttributeDefinitions=[
                {"AttributeName": "order_uuid", "AttributeType": "S"}
            ],
            ProvisionedThroughput={
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            }
        )
        table.wait_until_exists()
        print(f"Table {table_name} created successfully.")
    except Exception as e:
        print(f"Error creating table {table_name}: {e}")

if __name__ == "__main__":
    create_samples_table()
    create_orders_table()