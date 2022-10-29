import unittest
from main import app


class TestHello(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.app = app.test_client()

    def test_hello(self):
        rv = self.app.get('/home')
        print("status", rv.status)
        if (rv.status == '200 OK'):
            self.assertEqual(rv.status, '200 OK')
            self.assertEqual(rv.data, b'Hello World!\n')
        else:
            print("ERROR", rv.status)

if __name__ == '__main__':
    unittest.main()
