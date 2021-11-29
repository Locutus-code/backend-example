"""
Note to reviewer: Imported code, this wasn't written as part of the exercise scope.

Generate swagger documentation for service.
"""

import os
import importlib
import json
from typing import List, Optional
from chalice.app import Blueprint, Chalice, Request, Response

from chalicelib.helpers.utils import get_base_url
from chalicelib.swagger_generator.swagger_generator import (
    PlanEncoder,
    TemplatedSwaggerGenerator,
)

api_docs = Blueprint(__name__)

response_content = """
<html>
    <head>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.20.0/swagger-ui.css">
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3.20.3/swagger-ui-bundle.js"></script>
        <script>

            function render() {
                var ui = SwaggerUIBundle({
                    spec:  $SPEC,
                    dom_id: '#swagger-ui',
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIBundle.SwaggerUIStandalonePreset
                    ]
                });
            }

        </script>
    </head>

    <body onload="render()">
        <div id="swagger-ui"></div>
    </body>
</html>
"""


def _get_swagger_spec(current_app: Chalice, current_request: Optional[Request] = None):
    model_modules = []

    models_dir = os.path.join(os.getcwd(), "chalicelib", "models", "payloads")

    for name in os.listdir(models_dir):
        if name.endswith(".py"):
            module = name[:-3]
            model_modules.append(
                importlib.import_module(f"chalicelib.models.payloads.{module}")
            )
    model_modules.append(importlib.import_module("chalicelib.models.generic"))

    definitions: List[dict] = []
    for module in model_modules:
        for (name, cls) in module.__dict__.items():
            try:
                definitions.append(cls.schema())
            except:
                # Ignore non-pydantic objects
                pass

    patched_attributes = {
        "schemes": ["http", "https"],
        "servers": [get_base_url(current_request)],
        "info": {"version": "0.0.1", "title": "Qvik Exercise API"},
    }

    config = TemplatedSwaggerGenerator().generate_swagger(
        app=current_app,
        model_definitions=definitions,
        patched_attributes=patched_attributes,
    )

    return config


@api_docs.route("/api-docs", methods=["GET"])
def get_docs():
    swagger_spec = json.dumps(
        _get_swagger_spec(
            current_app=api_docs.current_app, current_request=api_docs.current_request
        ),
        cls=PlanEncoder,
    )

    templated_spec = response_content.replace("$SPEC", swagger_spec)

    # output_format = api_docs.current_request.query_params.get("format", "").lower()
    output_format = "html"
    if output_format == "json":
        return Response(
            body=swagger_spec, status_code=200, headers={"Content-Type": "text/json"}
        )

    if not output_format or output_format == "html":
        return Response(
            body=templated_spec, status_code=200, headers={"Content-Type": "text/html"}
        )
