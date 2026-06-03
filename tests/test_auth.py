def test_register_page(client):
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Create Account' in response.data


def test_register_success(client):
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'StrongPass1',
        'confirm_password': 'StrongPass1',
    })
    assert response.status_code == 302


def test_register_password_mismatch(client):
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'StrongPass1',
        'confirm_password': 'DifferentPass1',
    })
    assert response.status_code == 200
    assert b'Passwords do not match' in response.data or b'danger' in response.data


def test_login_page(client):
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Sign In' in response.data


def test_login_success(client, user):
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'TestPass123',
    })
    assert response.status_code == 302


def test_login_invalid_password(client, user):
    response = client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'WrongPassword1',
    })
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data or b'danger' in response.data


def test_logout(client, user):
    client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'TestPass123',
    })
    response = client.get('/auth/logout')
    assert response.status_code == 302


def test_profile_requires_login(client):
    response = client.get('/auth/profile')
    assert response.status_code == 302


def test_profile_page(logged_in_client, user):
    response = logged_in_client.get('/auth/profile')
    assert response.status_code == 200
    assert b'testuser' in response.data or b'test@example.com' in response.data
