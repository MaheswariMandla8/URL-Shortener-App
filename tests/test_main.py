import pytest
from main import app, url_store, click_store

# Fixtures
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def clear_store():
    # Clear in-memory stores before each test
    url_store.clear()
    click_store.clear()

# Tests

def test_health_endpoint(client):
    res = client.get('/')
    assert res.status_code == 200
    data = res.get_json()
    assert data == {"status": "healthy", "service": "URL Shortener API"}


def test_shorten_valid_url(client):
    response = client.post('/api/shorten', json={'url': 'https://www.example.com'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'short_code' in data
    assert 'short_url' in data
    code = data['short_code']
    # Validate short_code format
    assert len(code) == 6
    assert code.isalnum()
    # Check in-memory storage
    assert code in url_store
    assert url_store[code]['url'] == 'https://www.example.com'


def test_shorten_missing_and_invalid_url(client):
    # Missing 'url'
    res1 = client.post('/api/shorten', json={})
    assert res1.status_code == 400
    err1 = res1.get_json()
    assert err1['error'] == "Missing 'url' in request body"

    # Invalid URL format
    res2 = client.post('/api/shorten', json={'url': 'not_a_url'})
    assert res2.status_code == 400
    err2 = res2.get_json()
    assert err2['error'] == "Invalid URL format"


def test_redirect_and_404(client):
    # Create a short code
    code = client.post('/api/shorten', json={'url': 'https://test.org/path'}).get_json()['short_code']
    # Valid redirect
    res = client.get(f'/{code}')
    assert res.status_code == 302
    assert res.headers['Location'] == 'https://test.org/path'

    # Invalid short code
    res404 = client.get('/abcdef')
    assert res404.status_code == 404


def test_stats_and_click_count(client):
    # Create a short code
    code = client.post('/api/shorten', json={'url': 'https://stats.example'}).get_json()['short_code']
    # Initial stats
    stats = client.get(f'/api/stats/{code}')
    assert stats.status_code == 200
    d = stats.get_json()
    assert d['url'] == 'https://stats.example'
    assert d['clicks'] == 0
    assert 'created_at' in d

    # Simulate clicks
    client.get(f'/{code}')
    client.get(f'/{code}')
    updated = client.get(f'/api/stats/{code}').get_json()
    assert updated['clicks'] == 2

    # Stats for invalid code
    bad = client.get('/api/stats/unknown')
    assert bad.status_code == 404
    assert bad.get_json()['error'] == 'Short code not found'
