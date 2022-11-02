import unittest

from main import app


class BasicTestCase(unittest.TestCase):

    def test_pages(self):
        tester = app.test_client(self)
        pages = ['/', 'about-us/', 'register/', 'login/', 'all-products/','/indiv-product/','/data_analyst_page/']
        for page in pages:

            response = tester.get(page, content_type='html/text')
            print("Page: ", page, "Response: ",response)

    class TestLogConfiguration(unittest.TestCase):
        """[config set up]
        """

        def test_INFO__level_log(self):
            """
            Verify log for INFO level
            """
            self.app = app
            self.client = self.app.test_client

            with self.assertLogs() as log:
                user_logs = self.client().get('/')
                self.assertEqual(len(log.output), 4)
                self.assertEqual(len(log.records), 4)
                self.assertIn('Info log information', log.output[0])


if __name__ == '__main__':
    unittest.main()
