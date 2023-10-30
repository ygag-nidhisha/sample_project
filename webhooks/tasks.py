import hmac, hashlib, json, requests, logging
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder

from sample_project.celery import app
from .utils import get_webhook

User = get_user_model()
# Get an instance of a logger
logger = logging.getLogger(__name__)


@app.task(bind=True)
def trigger_webhook(self, event, webhooks_ids, data):
    TriggerWebhook().run(event, webhooks_ids, data)


class TriggerWebhook:
    # The `TriggerWebhook` class is responsible for triggering a webhook with the specified event, user
    # ID, and data.
    def run(self, event, webhooks_ids, data):
        """
        The function takes an event, a list of webhook IDs, and data as input, and sends a POST request
        to each webhook with the event and data as payload.

        :param event: The `event` parameter is the name or identifier of the event that occurred. It
        could be something like "user_created" or "order_updated"
        :param webhooks_ids: The `webhooks_ids` parameter is a list of webhook IDs. These IDs are used
        to retrieve the corresponding webhooks from the database
        :param data: The `data` parameter is a dictionary that contains the data to be sent along with
        the event in the webhook payload. It can be any valid JSON serializable data
        """
        if event and webhooks_ids:
            webhooks = get_webhook(filter_context={"id__in": webhooks_ids})
            for webhook in webhooks:
                payload = json.dumps(
                    {"event": event, "data": data}, cls=DjangoJSONEncoder
                )
                if webhook:
                    webhook_response = requests.post(
                        url=webhook.url,
                        data=payload,
                        timeout=5,
                        headers=self.get_headers(webhook, payload),
                    )
                    if webhook_response.status_code // 100 == 2:
                        logger.info("Webhook success")
                    else:
                        logger.error("Some error occured")
                        logger.error(webhook_response.content)
                else:
                    logger.debug(f"{event} not subscribed by this user")
        else:
            logger.debug("No event or webhooks list")

    def get_headers(self, webhook, payload):
        """
        The function `get_headers` returns a dictionary of headers with the "content-type" set to
        "application/json" and the "X-Signature" set to the result of calling the `header_signature`
        method with the webhook secret and payload as arguments.

        :param webhook: The "webhook" parameter is an object that contains information about the
        webhook, such as its secret key
        :param payload: The payload parameter is the data that you want to send in the request body. It
        can be any JSON object or data that you want to include in the request
        :return: a dictionary object called "headers" which contains the "content-type" key-value pair
        and the "X-Signature" key-value pair.
        """
        headers = {"content-type": "application/json"}
        headers["X-Signature"] = self.header_signature(str(webhook.secret), payload)
        return headers

    @staticmethod
    def header_signature(secret, payload):
        """
        The `header_signature` function generates a HMAC SHA256 signature using a secret key and a
        payload.

        :param secret: The `secret` parameter is a string that represents a secret key used for
        generating the signature. It is used as the key for the HMAC algorithm
        :param payload: The payload is the data that you want to sign using the secret key. It can be
        any string or data that you want to protect and verify its integrity
        :return: The method is returning the signature, which is a string representing the HMAC-SHA256
        signature of the payload using the secret key.
        """
        signature = hmac.new(
            secret.encode("utf-8"), payload.encode("utf-8"), digestmod=hashlib.sha256
        ).hexdigest()
        return signature

    def get_user(self, user_id):
        """
        The function `get_user` retrieves a user object from the database based on the provided user ID.

        :param user_id: The user_id parameter is the unique identifier of a user. It is used to retrieve
        a specific user from the database
        :return: The User object with the specified user_id.
        """
        return User.objects.get(id=user_id)
