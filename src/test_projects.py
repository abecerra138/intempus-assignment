from unittest.mock import MagicMock, Mock, call, mock_open, patch
from fastapi import status
from fastapi.testclient import TestClient
import json
import multiprocessing


from src.main import app

class TestProjects:

    client = TestClient(app)


    @patch("builtins.open", new_callable=mock_open)
    def test_get_projects_no_data(self, mock_file_open: Mock):
        """
        Test GET /projects with an empty file
        """
        mock_data = json.dumps(None)
        mock_file_open.return_value.read.return_value = mock_data

        response = self.client.get("/projects")
        assert response.status_code == status.HTTP_200_OK

        assert response.json() == {"projects": []}

    @patch("builtins.open", new_callable=mock_open)
    def test_get_projects_data(self, mock_file_open: Mock):
        """
        Test GET /projects with a file with data
        """
        data = {"9584687": {"active": True,
          "department_id": None, "department_name": None, "end_date": None, 
          "file_upload_required": False, "geofence": False, "hour_budget": None, 
          "id": 9584687, "latitude": None, "logical_timestamp": 9148091966, 
          "longitude": None, "name": "test-put", "notes": "", "number": "1", 
          "number_of_children": 0}}
        
        mock_data = json.dumps(data)
        mock_file_open.return_value.read.return_value = mock_data

        response = self.client.get("/projects")
        assert response.status_code == status.HTTP_200_OK

        assert response.json() == {"projects": list(data.values())}

    @patch("builtins.open", new_callable=mock_open)
    def test_put_invalid_project(self, mock_file_open: Mock):
        """
        Test PUT /projects with an invalid project id path
        """
        data = {"9584687": {"active": True,
          "department_id": None, "department_name": None, "end_date": None, 
          "file_upload_required": False, "geofence": False, "hour_budget": None, 
          "id": 9584687, "latitude": None, "logical_timestamp": 9148091966, 
          "longitude": None, "name": "test-put", "notes": "", "number": "1", 
          "number_of_children": 0}}
        
        mock_data = json.dumps(data)
        mock_file_open.return_value.read.return_value = mock_data

        response = self.client.put("/projects/invalid", json={})
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @patch("builtins.open", new_callable=mock_open)
    def test_put_invalid_data(self, mock_file_open: Mock):
        """
        Test PUT /projects with an invalid field
        """
        data = {"9584687": {"active": True,
          "department_id": None, "department_name": None, "end_date": None, 
          "file_upload_required": False, "geofence": False, "hour_budget": None, 
          "id": 9584687, "latitude": None, "logical_timestamp": 9148091966, 
          "longitude": None, "name": "test-put", "notes": "", "number": "1", 
          "number_of_children": 0}}
        
        mock_data = json.dumps(data)
        mock_file_open.return_value.read.return_value = mock_data

        invalid_data = {"invalid_field": "test"}
        response = self.client.put("/projects", json=invalid_data)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    @patch("builtins.open", new_callable=mock_open)
    def test_put_projects(self, mock_file_open: Mock):
        """
        Test PUT /projects with valid data
        """
        mock_queue = Mock(spec=multiprocessing.Queue)
        data = {"9584687": {"active": True,
          "id": 9584687, "latitude": None, "logical_timestamp": 9148091966, 
          "longitude": None, "name": "test-put", "notes": "", "number": "1", 
          "number_of_children": 0}}
        
        new_data = {"9584687": {"active": True,
          "id": 9584687, "latitude": None, "logical_timestamp": 9148091966, 
          "longitude": None, "name": "test", "notes": "", "number": "1", 
          "number_of_children": 0}}

        mock_data = json.dumps(data)
        mock_file_open.return_value.read.return_value = mock_data

        updated_data = {"name": "test"}
        response = self.client.put("/projects/9584687", json=updated_data)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"projects": list(new_data.values())}

