from .schema import ConfigSchema,MailSchema, MailTestSchema, RetentionSchema, TwilioSchema
from .models import Config, MailSettings, TwilioSettings
from fastapi import APIRouter, status, HTTPException
from toolkits.twilio.twilio import TwilioToolkit
from toolkits.mail.mail import MailToolkit
from fastapi.param_functions import Depends
from apps.common import BothAuthParams
from starlette.responses import Response
from toolkits.influx import Influx
from config import settings

router: APIRouter = APIRouter()


@router.get("/", response_model=ConfigSchema)
async def get_config(app = Depends(BothAuthParams)):
    return Config.objects.get()


@router.get("/version")
async def get_version(app = Depends(BothAuthParams)):
    return {"version": settings.VERSION}


@router.get("/mail", response_model=MailSchema)
async def get_mail_config(app = Depends(BothAuthParams)):
    try:
        mail = MailSettings.objects.get()
    except MailSettings.DoesNotExist:
        mail = MailSettings()

    return mail


@router.get("/twilio", response_model=TwilioSchema, include_in_schema=False)
async def get_twilio_config(app = Depends(BothAuthParams)):
    try:
        twilio = TwilioSettings.objects.get()
    except TwilioSettings.DoesNotExist:
        twilio = TwilioSettings()
    
    return twilio


@router.post("/mail", status_code=status.HTTP_204_NO_CONTENT)
async def save_mail_settings(form: MailSchema, app = Depends(BothAuthParams)):
    try:
        try:
            mail = MailSettings.objects.get()
        except MailSettings.DoesNotExist:
            mail = MailSettings()

        if form.auth and (not form.email or not form.password):
            raise HTTPException(status_code=400, detail="Auth is Enabled. No email or password are provided")

        mail.auth = form.auth
        mail.smtp_server = form.smtp_server
        mail.mail_from = form.mail_from
        mail.smtp_port = form.smtp_port
        mail.ssl = form.ssl

        if mail.auth:
            mail.email = form.email
            mail.password = form.password
        else:
            mail.email = ""
            mail.password = ""

        mail.save()

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/test/mail")
async def test_mail_settings(form: MailTestSchema, app = Depends(BothAuthParams)):
    try:
        mail_toolkits = MailToolkit(form)

        subject: str = "LightOwl: Test Message"
        body: str = "<html><body>This is a test message from LightOwl</body></html>"

        response = mail_toolkits.send([form.to], subject, body)
        return response
    except Exception as err:
        print(err)
        raise HTTPException(status_code=500, detail=str(err))


@router.post("/retention")
async def update_retention(form: RetentionSchema, app = Depends(BothAuthParams)):
    try:
        influx = Influx()
        influx.change_retention_policy(form.retention_duration)

        config = Config.objects.get()
        config.retention_duration = form.retention_duration
        config.save()
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))


@router.post("/twilio", status_code=status.HTTP_204_NO_CONTENT, include_in_schema=False)
async def save_twilio_settings(form: TwilioSchema, app = Depends(BothAuthParams)):
    try:
        try:
            twilio = TwilioSettings.objects.get()
        except TwilioSettings.DoesNotExist:
            twilio = TwilioSettings()

        twilio.account_sid = form.account_sid
        twilio.auth_token = form.auth_token
        twilio.number_from = form.number_from
        twilio.save()

        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))


@router.post("/twilio/test", include_in_schema=False)
async def test_twilio(form: TwilioSchema, app = Depends(BothAuthParams)):
    twilio_toolkit = TwilioToolkit(form)
    twilio_toolkit.test()
