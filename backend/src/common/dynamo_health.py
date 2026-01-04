import os
import time
import boto3
from botocore.exceptions import BotoCoreError, ClientError

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DDB_RENTALS = os.getenv("DDB_RENTALS", "kcl-Rentals")

_last_check_at = 0.0
_last_ok = False
_ttl_ok = 15
_ttl_fail = 30

_dynamo = boto3.resource("dynamodb", region_name=AWS_REGION)

def dynamo_rentals_available(force: bool = False) -> bool:
    global _last_check_at, _last_ok

    now = time.time()
    ttl = _ttl_ok if _last_ok else _ttl_fail
    if not force and (now - _last_check_at) < ttl:
        return _last_ok

    _last_check_at = now

    try:
        tbl = _dynamo.Table(DDB_RENTALS)
        tbl.load()
        _last_ok = True
        return True
    except (ClientError, BotoCoreError, Exception) as e:
        print(f"[dynamo_health] Dynamo indisponível para rentals: {e}")
        _last_ok = False
        return False
