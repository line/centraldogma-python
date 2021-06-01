from requests import Response


class AuthorizationException(Exception):
    def __init__(self, response: Response):
        try:
            self.response = response.json()
            self.message = self.response["message"]
        except:
            print("The response format is not expected")

    def __str__(self):
        return self.response


class NotFoundException(Exception):
    def __init__(self, response: Response):
        try:
            self.response = response.json()
            self.exception = self.response["exception"]
            self.message = self.response["message"]
        except:
            print("The response format is not expected")

    def __str__(self):
        return self.response
