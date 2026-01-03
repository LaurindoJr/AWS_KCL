import uuid
import boto3
import os

DDB_AUDIT = os.getenv("DDB_AUDIT", "kcl-AuditLogs")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

dynamo = boto3.resource("dynamodb", region_name=AWS_REGION)
audit_tbl = dynamo.Table(DDB_AUDIT)

def log_audit(action: str, data: dict):
    try:
        audit_tbl.put_item(Item={"pk": action, "sk": str(uuid.uuid4()), "data": data})
    except Exception as e:
        print(f"ERROR in log_audit: {e}")


