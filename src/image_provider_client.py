import requests

IMAGE_PROVIDER_URL = "http://178.154.220.122:7777/images/"

def get_image(img_id: int, timeout: int = None) -> bytes:
    try:
        response = requests.get(f"{IMAGE_PROVIDER_URL}{img_id}", timeout=timeout)
        response.raise_for_status()
        return response.content
    except requests.Timeout:
        raise requests.Timeout("Timeout occurred while downloading image")
    except requests.RequestException as e:
        raise requests.RequestException(f"Error downloading image: {e}")
