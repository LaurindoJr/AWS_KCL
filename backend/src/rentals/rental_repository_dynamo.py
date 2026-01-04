import os
from datetime import date
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from src.rentals.rental_dto import CreateRentalDTO

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
DDB_RENTALS = os.getenv("DDB_RENTALS", "kcl-Rentals")

dynamo = boto3.resource("dynamodb", region_name=AWS_REGION)
tbl = dynamo.Table(DDB_RENTALS)

SEQ_PK = "SEQ"
SEQ_SK = "RENTAL_ID"

def _today_str() -> str:
    return date.today().isoformat()

class RentalRepositoryDynamo:
    def get_by_book_id(self, book_id: int):
        pk = f"BOOK#{book_id}"
        resp = tbl.query(
            KeyConditionExpression="pk = :pk AND begins_with(sk, :prefix)",
            ExpressionAttributeValues={":pk": pk, ":prefix": "RENTAL#"},
            ScanIndexForward=False,  # desc
        )
        items = resp.get("Items", [])

        out = []
        for it in items:
            out.append({
                "id": int(it["rental_id"]),
                "book_id": int(it["book_id"]),
                "renter": it["renter"],
                "start_date": date.fromisoformat(it["start_date"]),
                "end_date": date.fromisoformat(it["end_date"]) if it.get("end_date") else None,
                "status": it["status"],
            })
        return out

    def create(self, book_id: int, rental: CreateRentalDTO) -> int:
        seq = tbl.update_item(
            Key={"pk": SEQ_PK, "sk": SEQ_SK},
            UpdateExpression="SET #v = if_not_exists(#v, :zero) + :one",
            ExpressionAttributeNames={"#v": "value"},
            ExpressionAttributeValues={":zero": 0, ":one": 1},
            ReturnValues="UPDATED_NEW",
        )
        rental_id = int(seq["Attributes"]["value"])

        pk = f"BOOK#{book_id}"
        sk = f"RENTAL#{rental_id}"

        tbl.put_item(Item={
            "pk": pk,
            "sk": sk,
            "rental_id": rental_id,
            "book_id": book_id,
            "renter": rental.renter,
            "start_date": _today_str(),
            "end_date": None,
            "status": "OPEN",
        })

        return rental_id

    def return_rental(self, rental_id: int):
        lookup = tbl.get_item(Key={"pk": f"RENTAL#{rental_id}", "sk": "LOOKUP"}).get("Item")
        if not lookup:
            return None

        book_id = int(lookup["book_id"])
        pk = f"BOOK#{book_id}"
        sk = f"RENTAL#{rental_id}"

        resp = tbl.update_item(
            Key={"pk": pk, "sk": sk},
            UpdateExpression="SET end_date=:d, #s=:closed",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":d": _today_str(), ":closed": "CLOSED"},
            ReturnValues="ALL_NEW"
        )
        attrs = resp.get("Attributes")
        if not attrs:
            return None

        return {"book_id": int(attrs["book_id"]), "end_date": date.fromisoformat(attrs["end_date"])}

    def create_lookup(self, book_id: int, rental_id: int):
        tbl.put_item(Item={
            "pk": f"RENTAL#{rental_id}",
            "sk": "LOOKUP",
            "book_id": book_id,
        })
