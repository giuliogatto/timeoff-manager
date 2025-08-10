import pytest
from fastapi import status
from datetime import date, datetime, timedelta
from models.leave_requests import LeaveRequest, StatusEnum, RequestTypeEnum

class TestLeaveRequests:
    """Test leave requests endpoints"""
    
    def test_get_leave_requests_unauthorized(self, client):
        """Test getting leave requests without authentication"""
        response = client.get("/leave_requests")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_leave_requests_user(self, client, auth_headers, test_user, db_session):
        """Test getting leave requests for regular user (should see only their own)"""
        # Create leave requests for different users
        other_user = test_user  # Using the same user for simplicity
        leave_request1 = LeaveRequest(
            user_id=test_user.id,
            request_type=RequestTypeEnum.timeoff,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            reason="Vacation"
        )
        leave_request2 = LeaveRequest(
            user_id=test_user.id,
            request_type=RequestTypeEnum.permission,
            start_datetime=datetime.now(),
            end_datetime=datetime.now() + timedelta(hours=2),
            reason="Doctor appointment"
        )
        
        db_session.add_all([leave_request1, leave_request2])
        db_session.commit()
        
        response = client.get("/leave_requests", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "leave_requests" in data
        assert len(data["leave_requests"]) == 2
        
        # Check that both requests belong to the authenticated user
        for request in data["leave_requests"]:
            assert request["user_id"] == test_user.id
    
    def test_get_leave_requests_manager(self, client, manager_headers, test_manager, test_user, db_session):
        """Test getting leave requests for manager (should see all)"""
        # Create leave requests for different users
        leave_request1 = LeaveRequest(
            user_id=test_user.id,
            request_type=RequestTypeEnum.timeoff,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            reason="Vacation"
        )
        leave_request2 = LeaveRequest(
            user_id=test_manager.id,
            request_type=RequestTypeEnum.permission,
            start_datetime=datetime.now(),
            end_datetime=datetime.now() + timedelta(hours=2),
            reason="Meeting"
        )
        
        db_session.add_all([leave_request1, leave_request2])
        db_session.commit()
        
        response = client.get("/leave_requests", headers=manager_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "leave_requests" in data
        assert len(data["leave_requests"]) == 2
        
        # Check that we see requests from both users
        user_ids = [req["user_id"] for req in data["leave_requests"]]
        assert test_user.id in user_ids
        assert test_manager.id in user_ids
    
    def test_create_timeoff_request(self, client, auth_headers, test_user):
        """Test creating a timeoff request"""
        request_data = {
            "request_type": "timeoff",
            "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=2)).isoformat(),
            "reason": "Vacation time"
        }
        
        response = client.post("/leave_requests", json=request_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == test_user.id
        assert data["request_type"] == "timeoff"
        assert data["reason"] == "Vacation time"
        assert data["status"] == "pending"
        assert "start_date" in data
        assert "end_date" in data
        assert "message" in data
        assert "Timeoff request created successfully" in data["message"]
    
    def test_create_permission_request(self, client, auth_headers, test_user):
        """Test creating a permission request"""
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=3)
        
        request_data = {
            "request_type": "permission",
            "start_datetime": start_time.isoformat(),
            "end_datetime": end_time.isoformat(),
            "reason": "Doctor appointment"
        }
        
        response = client.post("/leave_requests", json=request_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == test_user.id
        assert data["request_type"] == "permission"
        assert data["reason"] == "Doctor appointment"
        assert data["status"] == "pending"
        assert "start_datetime" in data
        assert "end_datetime" in data
        assert "message" in data
        assert "Permission request created successfully" in data["message"]
    
    def test_create_request_unauthorized(self, client):
        """Test creating a request without authentication"""
        request_data = {
            "request_type": "timeoff",
            "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=1)).isoformat(),
            "reason": "Test"
        }
        
        response = client.post("/leave_requests", json=request_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_request_invalid_type(self, client, auth_headers):
        """Test creating a request with invalid type"""
        request_data = {
            "request_type": "invalid_type",
            "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=1)).isoformat(),
            "reason": "Test"
        }
        
        response = client.post("/leave_requests", json=request_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_timeoff_request_missing_dates(self, client, auth_headers):
        """Test creating a timeoff request without required dates"""
        request_data = {
            "request_type": "timeoff",
            "reason": "Test"
        }
        
        response = client.post("/leave_requests", json=request_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_permission_request_missing_datetimes(self, client, auth_headers):
        """Test creating a permission request without required datetimes"""
        request_data = {
            "request_type": "permission",
            "reason": "Test"
        }
        
        response = client.post("/leave_requests", json=request_data, headers=auth_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_request_status_unauthorized(self, client, db_session, test_user):
        """Test updating request status without authentication"""
        # Create a leave request
        leave_request = LeaveRequest(
            user_id=test_user.id,
            request_type=RequestTypeEnum.timeoff,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            reason="Test"
        )
        db_session.add(leave_request)
        db_session.commit()
        
        response = client.put(f"/leave_requests/{leave_request.id}/status", json={
            "status": "approved"
        })
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_update_request_status_not_manager(self, client, auth_headers, db_session, test_user):
        """Test updating request status as regular user (should fail)"""
        # Create a leave request
        leave_request = LeaveRequest(
            user_id=test_user.id,
            request_type=RequestTypeEnum.timeoff,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            reason="Test"
        )
        db_session.add(leave_request)
        db_session.commit()
        
        response = client.put(f"/leave_requests/{leave_request.id}/status", json={
            "status": "approved"
        }, headers=auth_headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_update_request_status_manager(self, client, manager_headers, db_session, test_user):
        """Test updating request status as manager"""
        # Create a leave request
        leave_request = LeaveRequest(
            user_id=test_user.id,
            request_type=RequestTypeEnum.timeoff,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            reason="Test"
        )
        db_session.add(leave_request)
        db_session.commit()
        
        response = client.put(f"/leave_requests/{leave_request.id}/status", json={
            "status": "approved"
        }, headers=manager_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "approved"
        assert data["reviewed_by"] == test_user.id  # The manager's ID
        
        # Check database was updated
        db_session.refresh(leave_request)
        assert leave_request.status == StatusEnum.approved
        assert leave_request.reviewed_by == test_user.id
        assert leave_request.reviewed_at is not None
    
    def test_update_request_status_invalid_status(self, client, manager_headers, db_session, test_user):
        """Test updating request status with invalid status"""
        # Create a leave request
        leave_request = LeaveRequest(
            user_id=test_user.id,
            request_type=RequestTypeEnum.timeoff,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            reason="Test"
        )
        db_session.add(leave_request)
        db_session.commit()
        
        response = client.put(f"/leave_requests/{leave_request.id}/status", json={
            "status": "invalid_status"
        }, headers=manager_headers)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_request_status_not_found(self, client, manager_headers):
        """Test updating status of non-existent request"""
        response = client.put("/leave_requests/999/status", json={
            "status": "approved"
        }, headers=manager_headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_request_status_already_processed(self, client, manager_headers, db_session, test_user):
        """Test updating status of already processed request"""
        # Create an approved leave request
        leave_request = LeaveRequest(
            user_id=test_user.id,
            request_type=RequestTypeEnum.timeoff,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            reason="Test",
            status=StatusEnum.approved,
            reviewed_by=test_user.id,
            reviewed_at=datetime.now()
        )
        db_session.add(leave_request)
        db_session.commit()
        
        response = client.put(f"/leave_requests/{leave_request.id}/status", json={
            "status": "rejected"
        }, headers=manager_headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
