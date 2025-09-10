import requests


def validate_http_url(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return f'{url} returned status code {response.status_code}'
    except requests.exceptions.Timeout:
        return f'Timeout occurred while trying to reach {url}'
    except requests.exceptions.ConnectionError:
        return f'Connection error occurred while trying to reach {url}'
    except Exception as e:
        return f'An unexpected error occurred while trying to reach {url}: {str(e)}'