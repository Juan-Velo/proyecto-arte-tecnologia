try:
    from serverless_wsgi import handle_request as handle
except ImportError:
    from serverless_wsgi import handle

from app import app


def handler(event, context):
    return handle(app, event, context)
