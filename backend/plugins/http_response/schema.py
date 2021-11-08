from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum
import validators
import ipaddress


class MethodEnum(str, Enum):
    GET = "GET"
    POST = "POST"
    OPTIONS = "OPTIONS"

class ResponseEnum(int, Enum):
    OK = 200
    PERMREDIRECT = 301
    TEMPREDIRECT = 302
    NOTAUTH = 401
    REFUSED = 403
    NOTFOUND = 404
    SERVDEFAULT = 500
    SERVERROR = 503
    UNREACHSERV = 504

    
class HTTPResponse(BaseModel):
    """
    This input plugin checks HTTP/HTTPS connections.
    """

    urls: List[str] = Field(
        title="URLs",
        description="List of urls to query."
    )

    http_proxy: str = Field(
        "",
        title="HTTP Proxy",
        description="Set http_proxy (telegraf uses the system wide proxy settings if it's not set)",
        advanced=True
    )

    response_timeout: float = Field(
        5.0,
        title="Response Timeout",
        description="Set response_timeouts",
        min=1.0,
    )

    method: MethodEnum = Field(
        'GET',
        title="Method",
        description='HTTP Request Method',
        advanced=True
    )

    follow_redirects: bool = Field(
        False,
        title="Follow Redirects",
        description="Whether to follow redirects from the server"
    )

    username: Optional[str] = Field(
        title="Username",
        description="Opitonal HTTP Basic Auth Credentials",
    )

    password: Optional[str] = Field(
        title="Password",
        description="Opitonal HTTP Basic Auth Credentials",
    )

    response_body_field: Optional[str] = Field(
        '',
        title="Response Body Field",
        description="Optional name of the field that will contain the body of the response. By default it is set to an empty String indicating that the body's content won't be added",
        advanced=True
    )

    response_body_max_size: Optional[int] = Field(
        32,
        title="Response Body Max Size",
        description='Maximum allowed HTTP response body size in bytes. 0 means to use the default of 32MiB. If the response body size exceeds this limit a "body_read_error" will be raised',
        advanced=True
    )

    response_string_match: Optional[str] = Field(
        '',
        title="Response String Match",
        description='Optional substring or regex match in body of the response (case sensitive). Examples : response_string_match = "\"service_status\": \"up\"", response_string_match = "ok", response_string_match = "\".*_status\".?:.?\"up\""',
        advanced=True
    )

    response_status_code: Optional[ResponseEnum] = Field(
        200,
        title="Expected Response Status Code",
        description='The status code of the response is compared to this value. If they match, the fiel "response_status_code_match" will be 1, otherwise it will be 0. If the expected status code is 0, the check is disabled and the field will not be added'
    )

    insecure_skip_verify: Optional[bool] = Field(
        False,
        title="Insecure Skip Verify",
        description="Use TLS but skip chain & host verification"
    )

    tls_server_name: Optional[str] = Field(
        '',
        title="TLS Server Name",
        description="Use the given name as the SNI server name on each URL",
        advanced=True
    )

    http_header_tags: Optional[str] = Field(
        '',
        title="HTTP Header Tags",
        description="If the http header is not present on the request, no corresponding tag will be added. If multiple instances of the http header are present, only the first value will be used",
        advanced=True
    )

    # interface: Optional[str] = Field(
    #     '',
    #     title="Interface",
    #     description="Interface to use when dialing an address",
    #     advanced=True
    # )

    @validator("urls")
    def validate_urls(cls, v):
        for i in v:
            try:
                ipaddress.ip_address(i)
            except ValueError:
                if not validators.url(i):
                    raise ValueError(f"{i} is not a valid IP Address or URL")

        return v
    
    class Config:
        color: str = "#f49b51"
        icon: str = "fa fa-route"
        metrics: dict = {
            "result_code": "success = 0, no such host = 1, ping error = 2"
        }
