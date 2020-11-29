import json
from base64 import b64decode
import uuid
import urllib.parse
import boto3

DATABASE_TABLE = "secrets"

db_table = boto3.resource("dynamodb").Table(DATABASE_TABLE)


def lambda_handler(event, context):
    print(event)
    method = event["requestContext"]["http"]["method"]
    if method == "GET" and event["rawPath"] == "/":
        return serve_index_page()
    elif method == "POST" and event["rawPath"] == "/create-secret":
        secret = b64decode(event["body"]) if event["isBase64Encoded"] else event["body"]
        secret = urllib.parse.parse_qs(secret.decode("utf-8"))["secret"][0]

        return store_secret_and_display_url(secret)
    #    elif event["rawPath"] == "/retrieve-secret":
    #        return
    else:
        return serve_404()


def serve_404():
    return {
        "statusCode": 404,
        "headers": {"Content-Type": "text/html"},
        "body": "Sorry, we could not find what you were looking for",
    }


def store_secret_and_display_url(secret):
    secret_id = uuid.uuid4()

    db_table.put_item(
        Item={"uuid": secret_id, "secret": secret,}
    )

    url = f"https://secrets.easee.io/retrieve-secret?id='{str(secret_id)}'"

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "text/html"},
        "body": f"Send this link to the recipient. It can only be used once! {url}",
    }


def serve_index_page():
    body = open("index.html").read()
    return {"statusCode": 200, "headers": {"Content-Type": "text/html"}, "body": body}
