from chalice import (
    Chalice,
    Response,
)
from chalice.app import ConvertToMiddleware

from aws_lambda_powertools import Logger, Tracer

from chalicelib.blueprints.users import usersapi

app = Chalice(app_name="chalice-python-template")
app.debug = True
logger = Logger()
tracer = Tracer()

app.register_middleware(ConvertToMiddleware(logger.inject_lambda_context))
app.register_middleware(ConvertToMiddleware(tracer.capture_lambda_handler))

app.register_blueprint(usersapi)


@app.route("/healthy")
def health_status():
    Response(status_code=200, body="OK")
