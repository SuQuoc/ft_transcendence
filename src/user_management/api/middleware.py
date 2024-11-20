import logging

logger = logging.getLogger("django.request")

class LogRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        protocol = "HTTPS" if request.is_secure() else "HTTP"
        logging.warning(f"Received a {protocol} request to {request.get_full_path()}")
        logging.warning(f"Headers: {dict(request.headers)}")

        # Check Content-Type for binary data
        if "application/json" in request.headers.get("Content-Type", "") or \
           "text/" in request.headers.get("Content-Type", ""):
            try:
                logging.warning(f"Body: {request.body.decode('utf-8')}")
            except UnicodeDecodeError:
                logging.warning("Body could not be decoded as UTF-8.")
        else:
            logging.warning("Body is binary or not decodable.")

        response = self.get_response(request)
        return response
