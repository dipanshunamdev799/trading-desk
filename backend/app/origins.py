"""Allow configured origins and same-origin requests through the local app proxy."""
from ipaddress import ip_address
from urllib.parse import urlsplit
from starlette.requests import HTTPConnection


def _origin(value):
    try:
        url=urlsplit(value)
        if url.scheme not in ('http','https') or not url.hostname or url.username is not None or url.password is not None or url.path not in ('','/') or url.query or url.fragment:
            return None
        return (url.scheme,url.hostname,url.port or (443 if url.scheme=='https' else 80))
    except (ValueError,TypeError):return None


def allowed_application_origin(connection:HTTPConnection,configured):
    value=connection.headers.get('origin')
    if value is None:return True  # Local CLI clients do not send browser origins.
    origin=_origin(value)
    if origin is None:return False
    if origin in {_origin(item) for item in configured}:return True
    try:
        if not connection.client or not ip_address(connection.client.host).is_loopback:return False
    except ValueError:return False
    if origin[1] not in ('localhost','127.0.0.1','::1'):return False
    # Fetch Metadata is browser-controlled. A cross-site page cannot opt into
    # this exception by inventing a forwarded host or choosing a local port.
    if connection.headers.get('sec-fetch-site')!='same-origin':return False
    scheme={'ws':'http','wss':'https'}.get(connection.scope['scheme'],connection.scope['scheme'])
    host=connection.headers.get('host','')
    if origin==_origin(scheme+'://'+host):return True
    forwarded_host=connection.headers.get('x-forwarded-host','')
    forwarded_scheme=connection.headers.get('x-forwarded-proto') or scheme
    return origin==_origin(forwarded_scheme+'://'+forwarded_host)
