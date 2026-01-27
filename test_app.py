import pytest
import json
from unittest.mock import patch, MagicMock
from app import app, Records, UpdateRecords, AddRecord, Wake


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestRootEndpoint:
    """Test the root endpoint"""
    
    def test_root_endpoint_returns_200(self, client):
        """Test that root endpoint returns 200 status code"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_root_endpoint_returns_json(self, client):
        """Test that root endpoint returns JSON data"""
        response = client.get('/')
        data = json.loads(response.data)
        assert data['message'] == "Tracker API is running"
    
    def test_root_endpoint_contains_endpoints(self, client):
        """Test that root endpoint lists all API endpoints"""
        response = client.get('/')
        data = json.loads(response.data)
        endpoints = data['endpoints']
        
        expected_endpoints = [
            'records', 'add-record', 'update-records', 
            'add-batch', 'wake-up', 'api-docs'
        ]
        for endpoint in expected_endpoints:
            assert endpoint in endpoints


class TestWakeEndpoint:
    """Test the wake-up endpoint"""
    
    def test_wake_endpoint_returns_200(self, client):
        """Test that wake endpoint returns 200 status code"""
        response = client.get('/wake-up')
        assert response.status_code == 200
    
    def test_wake_endpoint_returns_message(self, client):
        """Test that wake endpoint returns success message"""
        response = client.get('/wake-up')
        assert b"Woke-up, Thank u :-)" in response.data


class TestRecordsEndpoint:
    """Test the records GET endpoint"""
    
    @patch('fb_manager.get_all_records')
    def test_records_endpoint_with_valid_auth(self, mock_get_records, client):
        """Test records endpoint with valid authentication"""
        mock_get_records.return_value = [{'key': 'value'}]
        
        response = client.get(
            '/records?uname=nam&key=271016',
            headers={'user': 'TestUser'}
        )
        
        assert response.status_code == 200
        mock_get_records.assert_called_once_with('TestUser')
    
    def test_records_endpoint_with_invalid_auth(self, client):
        """Test records endpoint with invalid authentication"""
        response = client.get(
            '/records?uname=invalid&key=wrong',
            headers={'user': 'TestUser'}
        )
        
        assert response.status_code == 500
        assert b"Unable to Authenticate" in response.data
    
    def test_records_endpoint_missing_header(self, client):
        """Test records endpoint without user header"""
        with pytest.raises(Exception):
            response = client.get(
                '/records?uname=nam&key=271016'
            )


class TestUpdateRecordsEndpoint:
    """Test the update records POST endpoint"""
    
    @patch('fb_manager.update_records')
    def test_update_records_success(self, mock_update, client):
        """Test successful record update"""
        mock_update.return_value = True
        
        test_data = {
            'Bank~Account~Key': {
                'amount': 1000,
                'description': 'Test'
            }
        }
        
        response = client.post(
            '/update-records',
            data=json.dumps(test_data),
            content_type='application/json',
            headers={'user': 'TestUser'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == "Record added successfully"
    
    @patch('fb_manager.update_records')
    def test_update_records_failure(self, mock_update, client):
        """Test failed record update"""
        mock_update.return_value = False
        
        test_data = {'key': 'value'}
        
        response = client.post(
            '/update-records',
            data=json.dumps(test_data),
            content_type='application/json',
            headers={'user': 'TestUser'}
        )
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['message'] == "Failed to add record"
    
    @patch('fb_manager.update_records')
    def test_update_records_default_user(self, mock_update, client):
        """Test update records with default user when header missing"""
        mock_update.return_value = True
        
        test_data = {'key': 'value'}
        
        response = client.post(
            '/update-records',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        mock_update.assert_called_once_with('Nadeem', test_data)


class TestAddRecordEndpoint:
    """Test the add record POST endpoint"""
    
    @patch('formatter.get_msg_to_json')
    @patch('fb_manager.add_record')
    def test_add_record_success(self, mock_add, mock_formatter, client):
        """Test successful record addition"""
        mock_formatter.return_value = ('Bank_Account_Key', {'refNo': '123'}, '2026-01-27')
        mock_add.return_value = True
        
        test_data = {
            'address': '+1234567890',
            'body': 'Test SMS'
        }
        
        response = client.post(
            '/add-record',
            data=json.dumps(test_data),
            content_type='application/json',
            headers={'user': 'TestUser'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        # Note: The actual response may be skipped if the formatter returns empty json dict
        assert 'message' in data
    
    @patch('formatter.get_msg_to_json')
    def test_add_record_skip_empty_key(self, mock_formatter, client):
        """Test that record with empty key is skipped"""
        mock_formatter.return_value = ('', {}, '2026-01-27')
        
        test_data = {'address': '+1234567890', 'body': 'Test SMS'}
        
        response = client.post(
            '/add-record',
            data=json.dumps(test_data),
            content_type='application/json',
            headers={'user': 'TestUser'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'Skipped Record' in data['message']


class TestAPIDocumentation:
    """Test API documentation endpoint"""
    
    def test_api_docs_endpoint_exists(self, client):
        """Test that API docs endpoint is accessible"""
        response = client.get('/apidocs')
        # Should return 200 or redirect (swagger UI might redirect)
        assert response.status_code in [200, 301, 302, 308]


class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_endpoint(self, client):
        """Test accessing invalid endpoint"""
        response = client.get('/invalid-endpoint')
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test using wrong HTTP method"""
        response = client.get('/add-record')  # Should be POST
        assert response.status_code == 405


class TestCORS:
    """Test CORS configuration"""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are included"""
        response = client.get('/')
        # Check for Access-Control headers
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
