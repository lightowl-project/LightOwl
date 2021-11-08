from fastapi.exceptions import HTTPException
from starlette import status
from twilio.base.exceptions import TwilioRestException
from apps.config.schema import TwilioSchema
from twilio.rest import Client


class TwilioToolkit:
    def __init__(self, twilio_config: TwilioSchema):
        self.config = twilio_config

    def _get_client(self):
        return Client(self.config.account_sid, self.config.auth_token)

    def test(self):
        client = self._get_client()
        try:
            response = client.incoming_phone_numbers.create(
                phone_number='+15005550006'
            )
            return response
        except TwilioRestException as err:
            if err.status == 401:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Twilio Credentials")
