import unittest
from flask import json
from service import app, talisman

BASE_URL = "/accounts"
HTTPS_ENVIRON = {'wsgi.url_scheme': 'https'}

class TestAccountRoutes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.testing = True
        cls.client = app.test_client()
        # Disable forced HTTPS for testing
        talisman.force_https = False

    def test_health_check(self):
        """Test the health check endpoint"""
        resp = self.client.get('/health')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json['status'], 'OK')

    def test_create_account(self):
        """Test creating a new account"""
        account_data = {
            "name": "John Doe",
            "email": "johndoe@example.com",
            "address": "123 Elm Street",
            "phone_number": "555-555-5555",
            "date_joined": "2023-01-01"
        }
        resp = self.client.post('/accounts', json=account_data)
        self.assertEqual(resp.status_code, 201)
        self.assertIn('Location', resp.headers)
        self.assertEqual(resp.json['name'], account_data['name'])

    def test_list_accounts(self):
        """Test listing all accounts"""
        resp = self.client.get('/accounts')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json, list)

    def test_get_account(self):
        """Test getting an account by id"""
        # Create an account first
        account_data = {
            "name": "John Doe",
            "email": "johndoe@example.com",
            "address": "123 Elm Street",
            "phone_number": "555-555-5555",
            "date_joined": "2023-01-01"
        }
        create_resp = self.client.post('/accounts', json=account_data)
        account_id = create_resp.json['id']

        # Get the account by id
        resp = self.client.get(f'/accounts/{account_id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json['name'], account_data['name'])

    def test_update_account(self):
        """Test updating an account"""
        # Create an account first
        account_data = {
            "name": "John Doe",
            "email": "johndoe@example.com",
            "address": "123 Elm Street",
            "phone_number": "555-555-5555",
            "date_joined": "2023-01-01"
        }
        create_resp = self.client.post('/accounts', json=account_data)
        account_id = create_resp.json['id']

        # Update the account
        updated_data = {
            "name": "Jane Doe",
            "email": "janedoe@example.com",
            "address": "456 Maple Street",
            "phone_number": "555-555-5556",
            "date_joined": "2023-02-01"
        }
        resp = self.client.put(f'/accounts/{account_id}', json=updated_data)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json['name'], updated_data['name'])

    def test_delete_account(self):
        """Test deleting an account"""
        # Create an account first
        account_data = {
            "name": "John Doe",
            "email": "johndoe@example.com",
            "address": "123 Elm Street",
            "phone_number": "555-555-5555",
            "date_joined": "2023-01-01"
        }
        create_resp = self.client.post('/accounts', json=account_data)
        account_id = create_resp.json['id']

        # Delete the account
        resp = self.client.delete(f'/accounts/{account_id}')
        self.assertEqual(resp.status_code, 204)

    def test_root_url_security_headers(self):
        """Test that the root URL returns security headers"""
        resp = self.client.get('/', environ_overrides=HTTPS_ENVIRON)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('X-Frame-Options', resp.headers)
        self.assertEqual(resp.headers['X-Frame-Options'], 'SAMEORIGIN')
        self.assertIn('X-Content-Type-Options', resp.headers)
        self.assertEqual(resp.headers['X-Content-Type-Options'], 'nosniff')
        self.assertIn('Content-Security-Policy', resp.headers)
        self.assertEqual(resp.headers['Content-Security-Policy'], "default-src 'self'; object-src 'none'")
        self.assertIn('Referrer-Policy', resp.headers)
        self.assertEqual(resp.headers['Referrer-Policy'], 'strict-origin-when-cross-origin')

if __name__ == '__main__':
    unittest.main()
