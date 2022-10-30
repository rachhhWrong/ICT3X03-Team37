import unittest

from main import app


class BasicTestCase(unittest.TestCase):

    def test_pages(self):
        tester = app.test_client(self)
        pages = ['/', 'about-us/', 'register/', 'login/', 'all-goods/']
        for page in pages:
            response = tester.get(page, content_type='html/text')
            print(response)



if __name__ == '__main__':
    unittest.main()
