from rest_framework.views import exception_handler


def strapi_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None

    detail = response.data
    if isinstance(detail, dict) and "detail" in detail:
        message = detail["detail"]
    elif isinstance(detail, list) and detail:
        message = detail[0]
    else:
        message = detail

    if hasattr(message, "__str__"):
        message = str(message)

    response.data = {"error": {"message": message, "status": response.status_code}}
    return response
