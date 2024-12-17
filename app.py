from flask import Flask, request, jsonify
import uuid
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)

# DynamoDB setup
dynamodb = boto3.resource("dynamodb", region_name="us-west-2")
samples_table = dynamodb.Table("Samples")
orders_table = dynamodb.Table("Orders")

# Constants for sample statuses
STATUS_ORDERED = "ORDERED"
STATUS_FAILED = "FAILED"
STATUS_SHIPPED = "SHIPPED"

# Service layer logic
def get_sample(sample_uuid):
    try:
        response = samples_table.get_item(Key={"sample_uuid": sample_uuid})
        return response.get("Item")
    except ClientError as e:
        app.logger.error(f"Error getting sample {sample_uuid}: {e}")
        return None

def save_sample(sample):
    try:
        samples_table.put_item(Item=sample)
    except ClientError as e:
        app.logger.error(f"Error saving sample {sample['sample_uuid']}: {e}")

def get_order(order_uuid):
    try:
        response = orders_table.get_item(Key={"order_uuid": order_uuid})
        return response.get("Item")
    except ClientError as e:
        app.logger.error(f"Error getting order {order_uuid}: {e}")
        return None

def save_order(order):
    try:
        orders_table.put_item(Item=order)
    except ClientError as e:
        app.logger.error(f"Error saving order {order['order_uuid']}: {e}")

@app.route("/")
def home():
  return "Hello World"

# API 1: Place Order
@app.route("/place_order", methods=["POST"])
def place_order():
    data = request.get_json()
    # generate new id
    order_uuid = str(uuid.uuid4())
    repeat_sample_uuids = []

    for sample in data["order"]:
        sample_uuid = sample["sample_uuid"]
        if get_sample(sample_uuid):
            repeat_sample_uuids.append(sample_uuid)
        else:
            new_sample = {
                "sample_uuid": sample_uuid,
                "sequence": sample["sequence"],
                "status": STATUS_ORDERED,
                "qc": None,
                "plate_id": None,
                "well": None,
                "order_uuid": order_uuid
            }
            save_sample(new_sample)

    if repeat_sample_uuids:
        return jsonify({"repeat_sample_uuids": repeat_sample_uuids}), 400

    save_order({"order_uuid": order_uuid, "samples": [sample["sample_uuid"] for sample in data["order"]]})
    return jsonify({"order_uuid": order_uuid}), 201

# API 2: List Orders to Process
@app.route("/list_orders_to_process", methods=["GET"])
def list_orders_to_process():
    try:
        response = samples_table.scan()
        samples_to_make = [
            {"sample_uuid": item["sample_uuid"], "sequence": item["sequence"]}
            for item in response["Items"] 
            if item["status"] == STATUS_ORDERED
        ][:96]
        return jsonify({"samples_to_make": samples_to_make}), 200
    except ClientError as e:
        app.logger.error(f"Error listing orders to process: {e}")
        return jsonify({"error": "Could not retrieve orders"}), 500

# API 3: Log QC Results of Processed Orders
@app.route("/log_qc_results", methods=["POST"])
def log_qc_results():
    from decimal import Decimal
    data = request.get_json()

    for sample_data in data["samples_made"]:
        sample_uuid = sample_data["sample_uuid"]
        sample = get_sample(sample_uuid)
        if sample:
            sample.update({
                "qc": {
                    "qc_1": Decimal(str(sample_data["qc_1"])),
                    "qc_2": Decimal(str(sample_data["qc_2"])),
                    "qc_3": sample_data["qc_3"]
                },
                "plate_id": sample_data["plate_id"],
                "well": sample_data["well"],
                # check all three qc metrics to see if samples pass or fail.
                "status": STATUS_FAILED if sample_data["qc"]["qc_1"] < 10.0 or sample_data["qc"]["qc_2"] < 5.0 or sample_data["qc"]["qc_3"] == "FAIL" else sample["status"]
            })
            save_sample(sample)

    return jsonify({"status": "QC results logged"}), 200

# API 4: List Samples that Should be Shipped
@app.route("/list_samples_to_ship", methods=["GET"])
def list_samples_to_ship():
    try:
        response = samples_table.scan()
        samples_to_ship = [
            {
                "sample_uuid": item["sample_uuid"],
                "plate_id": item["plate_id"],
                "well": item["well"]
            }
            # check for any qc failures. if none then return record of samples to ship.
            for item in response["Items"]
            if item.get("qc") and item["qc"]["qc_3"] == "PASS" and item["status"] != STATUS_FAILED and item["status"] != STATUS_SHIPPED
        ]
        return jsonify({"samples_to_ship": samples_to_ship}), 200
    except ClientError as e:
        app.logger.error(f"Error listing samples to ship: {e}")
        return jsonify({"error": "Could not retrieve samples"}), 500

# API 5: Record Samples as Shipped
@app.route("/record_samples_as_shipped", methods=["POST"])
def record_samples_as_shipped():
    data = request.get_json()

    for sample_uuid in data["samples_shipped"]:
        sample = get_sample(sample_uuid)
        if sample and sample["status"] != STATUS_SHIPPED:
            sample["status"] = STATUS_SHIPPED
            save_sample(sample)

    return jsonify({"status": "Samples marked as shipped"}), 200

# Stretch Goal: Report Sample Statuses in Order
@app.route("/report_sample_statuses", methods=["GET"])
def report_sample_statuses():
    data = request.get_json()
    order_uuid = data["order_uuid_to_get_sample_statuses_for"]

    order = get_order(order_uuid)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    sample_statuses = [
        {"sample_uuid": sample_uuid, "status": get_sample(sample_uuid)["status"]}
        for sample_uuid in order["samples"]
    ]

    return jsonify({"sample_statuses": sample_statuses}), 200

if __name__ == "__main__":
    app.run(debug=False)

