import unittest
import sqlite3
from court_data_fetcher import app, init_db

class TestCourtDataFetcher(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        init_db()

    def test_db_init(self):
        conn = sqlite3.connect('court_data.db')
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='queries'")
        self.assertIsNotNone(c.fetchone())
        conn.close()

    def test_index_route(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Court Data Fetcher', response.data)

if __name__ == '__main__':
    unittest.main()