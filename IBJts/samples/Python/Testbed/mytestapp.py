from ibapi.wrapper import EWrapper
from ibapi.client import EClient
from ibapi.utils import iswrapper


class TestWrapper(EWrapper):
    def __init__(self):
        EWrapper.__init__(self)


class TestClient(EClient):
    def __init__(self, wrapper):
        EClient.__init__(self, wrapper)


class TestApp(TestClient, TestWrapper):
    def __init__(self):
        TestWrapper.__init__(self)
        TestClient.__init__(self,wrapper=self)


if __name__ == '__main__':
    app = TestApp()
    app.connect(host="127.0.0.1", port=args.port, clientId=0)
