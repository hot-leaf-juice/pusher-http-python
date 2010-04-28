import unittest, re, httplib, time, cgi
from nose.tools import *
import mox
import pusher

class PropertiesTest(unittest.TestCase):
    def setUp(self):
        pusher.app_id = 'test-global-app-id'
        pusher.key = 'test-global-key'
        pusher.secret = 'test-global-secret'

    def tearDown(self):
        pusher.app_id = 'api.pusherapp.com'
        pusher.key = None
        pusher.secret = None


    #
    # Using globals
    #
    
    def test_global_app_id(self, *args):
        eq_(pusher.Pusher().app_id, 'test-global-app-id')

    def test_global_key(self):
        eq_(pusher.Pusher().key, 'test-global-key')

    def test_global_secret(self):
        eq_(pusher.Pusher().secret, 'test-global-secret')


    #
    # Using instance-specific parameters
    #

    def test_instance_app_id(self):
        eq_(p().app_id, 'test-app-id')

    def test_instance_key(self):
        eq_(p().key, 'test-key')

    def test_instance_secret(self):
        eq_(p().secret, 'test-secret')


class ChannelTest(unittest.TestCase):
    def setUp(self):
        self.mox = mox.Mox()

    def tearDown(self):
        self.mox.UnsetStubs()

    def test_access_to_channels(self):
        channel = p()['test-channel']
        eq_(channel.__class__, pusher.Channel)
        eq_(channel.name, 'test-channel')

    def test_trigger(self):
        channel = p()['test-channel']
        mock_response = self.mox.CreateMock(httplib.HTTPResponse)
        mock_response.read()
        self.mox.StubOutWithMock(httplib.HTTPConnection, '__init__')
        httplib.HTTPConnection.__init__('api.pusherapp.com', 80)
        self.mox.StubOutWithMock(httplib.HTTPConnection, 'request')
        httplib.HTTPConnection.request('POST', mox.Func(query_assertion), '{"param2": "value2", "param1": "value1"}')
        self.mox.StubOutWithMock(httplib.HTTPConnection, 'getresponse')
        httplib.HTTPConnection.getresponse().AndReturn(mock_response)
        self.mox.StubOutWithMock(time, 'time')
        time.time().AndReturn(1272382015)
        self.mox.ReplayAll()
        channel.trigger('test-event', {'param1': 'value1', 'param2': 'value2'})
        self.mox.VerifyAll()

def query_assertion(path_and_query):
    path, query_string = path_and_query.split('?')
    ok_(re.search('^/apps/test-app-id/channels/test-channel/events', path))
    expected_query = {
        'auth_version': '1.0',
        'auth_key': 'test-key',
        'auth_timestamp': '1272382015',
        'auth_signature': 'cf0b2a9890c2f0e2300f34d1c68efc8faad86b9d8ae35de1917d3b21176e5793',
        'body_md5': 'd173e46bb2a4cf2d48a10bc13ec43d5a',
        'name': 'test-event',
    }

    for name, value in cgi.parse_qsl(query_string):
        eq_(value, expected_query[name])
    return True

def p(*args):
    return pusher.Pusher(app_id='test-app-id', key='test-key', secret='test-secret')