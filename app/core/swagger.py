from fastapi.openapi.utils import get_openapi


def custom_openapi(app):

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault(
                "security",
                [
                    {
                        "BearerAuth": []
                    }
                ],
            )

    app.openapi_schema = openapi_schema

    return app.openapi_schema