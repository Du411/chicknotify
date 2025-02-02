import pytest
from unittest.mock import Mock, patch
from app.services.user_service import UserService
from app.schemas.auth import UserRegister, UserLogin, UserUpdate
from fastapi import HTTPException
from app.models.users import User

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def user_service(mock_db):
    return UserService(mock_db)

def test_register_user_success(user_service, mock_db):
    user_data = UserRegister(
        username="abcde",
        email="abcde@example.com",
        password="password123",
        notification_type_id=1
    )
    

    mock_db.query.return_value.filter.return_value.first.return_value = None

    response = user_service.register_user(user_data)

    assert response["message"] == "register success"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()

def test_register_duplicate_username(user_service, mock_db):
    user_data = UserRegister(
        username="abcde",
        email="abcde@example.com",
        password="password123",
        notification_type_id=1
    )
    
    mock_db.query.return_value.filter.return_value.first.return_value = User()
    
    with pytest.raises(HTTPException) as exc:
        user_service.register_user(user_data)
    assert exc.value.status_code == 400
    assert "username is already used" in exc.value.detail

def test_login_user_success(user_service, mock_db):
    login_data = UserLogin(
        username="abcde",
        password="password123"
    )
    
    mock_user = Mock()
    mock_user.password = "hash_password123" 
    mock_user.user_id = 1
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    with patch('app.services.user_service.verify_password', return_value=True):
        response = user_service.login_user(login_data)
    
    assert "access_token" in response

def test_login_user_invalid_credentials(user_service, mock_db):
    login_data = UserLogin(
        username="testuser",
        password="wrongpass"
    )
    
    mock_user = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    with patch('app.services.user_service.verify_password', return_value=False):
        with pytest.raises(HTTPException) as exc:
            user_service.login_user(login_data)
        assert exc.value.status_code == 401

def test_update_user_password(user_service, mock_db):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.password = "hashed_old_password"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    update_data = UserUpdate(
        old_password="oldpassword123",
        password="newpassword123",
        notification_type_id=1,
        email="abcde@example.com"
    )

    with patch('app.services.user_service.verify_password', return_value=True), \
         patch('app.services.user_service.get_password_hash', return_value="hashed_new_password"):
        response = user_service.update_user(update_data, mock_user.user_id)
    
    assert response["message"] == "update success"
    mock_db.commit.assert_called_once()

def test_update_user_wrong_old_password(user_service, mock_db):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.password = "hashed_password"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    update_data = UserUpdate(
        old_password="wrongpass123",
        password="newpassword123",
        notification_type_id=1,
        email="abcde@example.com"
    )

    with patch('app.services.user_service.verify_password', return_value=False):
        with pytest.raises(HTTPException) as exc:
            user_service.update_user(update_data, mock_user.user_id)
    
    assert exc.value.status_code == 401
    assert "Old password is incorrect" in exc.value.detail

@pytest.mark.asyncio
async def test_get_user_notification_preferences(user_service, mock_db):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.notification_type_id = 1
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    mock_notification_type = Mock()
    mock_notification_type.type = "email"
    mock_notification_type.description = "Email notification"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_notification_type

    preferences = await user_service.get_user_notification_preferences(mock_user.user_id)
    assert preferences.user_id == mock_user.user_id
    assert preferences.notification_type == "email"

def test_update_user_telegram_id(user_service, mock_db):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.email = "abcde@example.com"
    mock_user.password = "old_password123"
    mock_user.notification_type_id = 1


    mock_db.query.return_value.filter.return_value.first.side_effect = [
        mock_user,
        None, 
    ]

    update_data = UserUpdate(
        telegram_id="tele123",
        notification_type_id=1,
        email="abcde@example.com"
    )
    
    response = user_service.update_user(update_data, mock_user.user_id)
    assert response["message"] == "update success"
    mock_db.commit.assert_called()

def test_update_user_discord_id(user_service, mock_db):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.email = "abcde@example.com"
    mock_user.password = "old_password123"
    mock_user.notification_type_id = 1

    mock_db.query.return_value.filter.return_value.first.side_effect = [
        mock_user,
        None,
    ]

    update_data = UserUpdate(
        discord_id="disc123",
        notification_type_id=1,
        email="abcde@example.com"
    )
    
    response = user_service.update_user(update_data, mock_user.user_id)
    assert response["message"] == "update success"
    mock_db.commit.assert_called()

def test_update_multiple_fields(user_service, mock_db):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.email = "abcde@example.com"
    mock_user.password = "hashed_old_password123"
    mock_user.notification_type_id = 1

    mock_db.query.return_value.filter.return_value.first.side_effect = [
        mock_user,
        None,
        None,
    ]

    update_data = UserUpdate(
        email="abcde@example.com",
        telegram_id="tele789",
        discord_id="disc789",
        notification_type_id=2,
        old_password="password123",
        password="newpassword123"
    )

    with patch('app.services.user_service.verify_password', return_value=True), \
         patch('app.services.user_service.get_password_hash', return_value="hashed_new_password"):
        response = user_service.update_user(update_data, mock_user.user_id)

    assert response["message"] == "update success"
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_profile(user_service, mock_db):
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.username = "abcde"
    mock_user.email = "abcde@example.com"
    mock_user.telegram_id = "tele123"
    mock_user.discord_id = "disc123"
    mock_user.notification_type_id = 1
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    profile = await user_service.get_user_profile(mock_user.user_id)
    assert profile.username == "abcde"
    assert profile.email == "abcde@example.com"
    assert profile.telegram_id == "tele123"
    assert profile.discord_id == "disc123"
    assert profile.notification_type_id == 1

@pytest.mark.asyncio
async def test_delete_user_success(user_service, mock_db):
    user_id = 1
    
    mock_user = Mock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user
    
    response = await user_service.delete_user(user_id)
    
    assert response["message"] == "User and all related data deleted successfully"
    mock_db.delete.assert_called_once_with(mock_user)
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_delete_nonexistent_user(user_service, mock_db):
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    with pytest.raises(HTTPException) as exc:
        await user_service.delete_user(1)
    assert exc.value.status_code == 404
    assert "User not found" in exc.value.detail 