import requests

def test_api_connection():
    api_url = 'http://localhost:7288/api/news'
    sample_data = [{
        'date': '2023-10-01',
        'title': 'Test Title',
        'summary': 'This is a test summary.',
        'link': 'https://example.com'
    }]

    try:
        response = requests.post(api_url, json=sample_data, verify=False)
        print(f'Response Status Code: {response.status_code}')
        print(f'Response Data: {response.text}')
    except requests.exceptions.RequestException as e:
        print(f"Failed to send data: {e}")

test_api_connection()
