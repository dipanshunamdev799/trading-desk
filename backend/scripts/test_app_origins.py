"""Local frontend proxy requests work without trusting cross-site browser requests."""
import sys
import unittest
from pathlib import Path
from starlette.requests import HTTPConnection

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.origins import allowed_application_origin


class ApplicationOriginTests(unittest.TestCase):
    configured=['http://localhost:3000','http://127.0.0.1:3000']
    def allowed(self,origin=None,headers=None,peer='127.0.0.1',scheme='http'):
        values={'host':'127.0.0.1:8000',**(headers or {})}
        if origin is not None:values['origin']=origin
        scope={'type':'websocket' if scheme=='ws' else 'http','scheme':scheme,'client':(peer,50000),'server':('127.0.0.1',8000),'path':'/','headers':[(k.encode(),v.encode()) for k,v in values.items()]}
        return allowed_application_origin(HTTPConnection(scope),self.configured)
    def test_configured_origins_and_local_cli_are_accepted(self):
        self.assertTrue(self.allowed());self.assertTrue(self.allowed('http://localhost:3000/'));self.assertTrue(self.allowed('http://127.0.0.1:3000'))
    def test_preview_same_origin_proxy_is_accepted(self):
        for host in ['127.0.0.1:3100','localhost:3101','[::1]:3000']:
            self.assertTrue(self.allowed('http://'+host,{'sec-fetch-site':'same-origin','x-forwarded-host':host,'x-forwarded-proto':'http'}))
    def test_websocket_preview_uses_the_same_origin_rule(self):
        self.assertTrue(self.allowed('http://127.0.0.1:3101',{'sec-fetch-site':'same-origin','x-forwarded-host':'127.0.0.1:3101','x-forwarded-proto':'http'},scheme='ws'))
    def test_next_rewrite_proxy_need_not_supply_forwarded_protocol(self):
        self.assertTrue(self.allowed('http://127.0.0.1:3112',{'sec-fetch-site':'same-origin','x-forwarded-host':'127.0.0.1:3112'}))
    def test_local_api_docs_can_use_their_own_origin(self):
        self.assertTrue(self.allowed('http://127.0.0.1:8000',{'sec-fetch-site':'same-origin'}))
    def test_preview_requires_matching_proxy_host_metadata_and_local_peer(self):
        origin='http://127.0.0.1:3101';proxy={'sec-fetch-site':'same-origin','x-forwarded-host':'127.0.0.1:3101','x-forwarded-proto':'http'}
        self.assertFalse(self.allowed(origin));self.assertFalse(self.allowed(origin,{**proxy,'sec-fetch-site':'cross-site'}))
        self.assertFalse(self.allowed(origin,{**proxy,'x-forwarded-host':'127.0.0.1:3100'}))
        self.assertFalse(self.allowed(origin,proxy,peer='192.0.2.1'))
    def test_foreign_opaque_and_malformed_origins_stay_blocked(self):
        for origin in ['null','https://untrusted.example','http://localhost.attacker.example:3101','http://user:pass@localhost:3000','http://localhost:3000/path','http://localhost:99999','http://localhost:3000?bad=1']:
            with self.subTest(origin=origin):
                self.assertFalse(self.allowed(origin,{'sec-fetch-site':'same-origin','x-forwarded-host':'localhost:3101','x-forwarded-proto':'http'}))


if __name__=='__main__':unittest.main()
