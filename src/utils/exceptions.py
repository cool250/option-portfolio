import logging


class APIException(Exception):
    """Exception raised for errors during API call.

    Args:
        api_respone(str): API endpoint response
    """

    def __init__(self, api_response):
        # Create a JSON response to parse error key
        response_dict = api_response.json()
        message = ""
        if response_dict.get("error") is not None:
            message = f"API Error : {response_dict.get('error')}"
        else:
            message = "API Error"
        logging.error(message)
        super().__init__(message)


class HaltCallbackException(Exception):
    """Generic exception for HaltCallbackException"""

    def __init__(self, msg, original_exception):
        super(HaltCallbackException, self).__init__(msg + (": %s" % original_exception))
        self.original_exception = original_exception
        logging.error(self.original_exception)
