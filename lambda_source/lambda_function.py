import json
import html
import time
from base64 import b64decode
import uuid
import urllib.parse
import boto3
from boto3.dynamodb.conditions import Key


DATABASE_TABLE = "secrets"

db_table = boto3.resource("dynamodb").Table(DATABASE_TABLE)


def _render(content, status_code=200, content_type="text/html"):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": content_type},
        "body": content,
    }


def _serve_static_file(file_path, status_code=200, content_type="text/html"):
    with open(file_path) as fh:
        return _render(fh.read(), status_code=status_code, content_type=content_type)


def _not_found():
    return _serve_main_html("<p>Sorry, we could not find what you were looking for</p>", status_code=404)


def _serve_main_html(content, status_code=200):
    with open("index.html") as fh:
        main = fh.read().replace("{content}", content)
    return _render(main, status_code=status_code)


def _serve_template(template_file, variables=None, status_code=200):
    if variables is None:
        variables = {}
    with open(template_file) as fh:
        contents = fh.read().format(**variables)
    return _serve_main_html(contents, status_code=status_code)


def lambda_handler(event, context):
    print(event["rawPath"])

    method = event["requestContext"]["http"]["method"]

    if method == "GET" and event["rawPath"] == "/":
        return _serve_template("create.html")

    elif method == "POST" and event["rawPath"] == "/create-secret":
        secret = b64decode(event["body"]) if event["isBase64Encoded"] else event["body"]
        secret = urllib.parse.parse_qs(secret.decode("utf-8"))["secret"][0]
        return store_secret_and_display_url(secret)

    elif event["rawPath"] == "/retrieve-secret":
        secret_id = event.get("queryStringParameters", {}).get("id", None)
        if secret_id is None:
            return _not_found()
        else:
            return retrieve_destroy_and_display_secret(secret_id)

    elif event["rawPath"] == "/favicon.ico":
        return _serve_static_file("favicon.ico", content_type="image/x-icon")

    return _not_found()


def store_secret_and_display_url(secret, expire_in_hours=168):
    secret_id = uuid.uuid4().hex

    db_table.put_item(
        Item={
            "uuid": secret_id,
            "secret": secret,
            "expireAt": int(time.time()) + expire_in_hours * 3600,
        }
    )

    url = f"https://secrets.easee.io/retrieve-secret?id={secret_id}"

    return _serve_template("show-url.html", {"url": url})


def retrieve_destroy_and_display_secret(secret_id):
    results = db_table.delete_item(
        Key={"uuid": secret_id},
        ReturnValues="ALL_OLD",
    )
    if "Attributes" not in results:
        return _not_found()
    secret = results["Attributes"]["secret"]

    return _serve_template("retrieve-secret.html", {"secret": html.escape(secret, quote=True)})
