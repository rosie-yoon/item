# platforms/shopee_client.py: Shopee API v2 implementation

from platforms.base_platform import BasePlatform
from config import SHOPEE_API_V2_URL
import requests
import time
import hmac
import hashlib
import rich

class ShopeeClient(BasePlatform):
    def __init__(self, partner_id, partner_key, access_token=None, shop_id=None):
        self.partner_id = partner_id
        self.partner_key = partner_key
        self.access_token = access_token
        self.shop_id = shop_id

    def _make_request(self, api_path, method, body=None, needs_access_token=True):
        """A helper method to make signed requests to the Shopee API."""
        timestamp = int(time.time())
        full_path = f"/api/v2{api_path}" # Standardize path generation
        
        common_params = f"?partner_id={self.partner_id}&timestamp={timestamp}"
        
        if needs_access_token:
            if self.access_token is None or self.shop_id is None:
                raise ValueError("Access token and shop_id are required for this API call.")
            base_string = f"{self.partner_id}{full_path}{timestamp}{self.access_token}{self.shop_id}"
            sign = hmac.new(self.partner_key.encode('utf-8'), base_string.encode('utf-8'), hashlib.sha256).hexdigest()
            url = f"{SHOPEE_API_V2_URL.rstrip('/')}{full_path}{common_params}&access_token={self.access_token}&shop_id={self.shop_id}&sign={sign}"
        else: # For auth-related calls
            base_string = f"{self.partner_id}{full_path}{timestamp}"
            sign = hmac.new(self.partner_key.encode('utf-8'), base_string.encode('utf-8'), hashlib.sha256).hexdigest()
            url = f"{SHOPEE_API_V2_URL.rstrip('/')}{full_path}{common_params}&sign={sign}"

        headers = {"Content-Type": "application/json"}
        
        try:
            if method.upper() == "POST":
                response = requests.post(url, json=body, headers=headers)
            else: # GET
                response = requests.get(url, headers=headers)
            
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            
            json_response = response.json()
            if json_response.get('error') and json_response.get('message'):
                rich.print(f"[bold red]Shopee API Error:[/bold red] {json_response['error']} - {json_response['message']}")
                return None
            return json_response

        except requests.exceptions.HTTPError as e:
            rich.print(f"[bold red]HTTP Error:[/bold red] {e.response.status_code} for URL: {e.response.url}")
            rich.print(f"Response Body: {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            rich.print(f"[bold red]API Request Error:[/bold red] {e}")
            return None

    def get_access_token(self, auth_code, shop_id):
        path = "/auth/get_access_token"
        body = {"code": auth_code, "shop_id": int(shop_id), "partner_id": self.partner_id}
        return self._make_request(path, method="POST", body=body, needs_access_token=False)

    def get_shop_info(self):
        path = "/shop/get_shop_info"
        return self._make_request(path, method="GET", body=None, needs_access_token=True)

    def get_product_details(self, item_id):
        path = "/product/get_item_base_info"
        body = {"item_id_list": [item_id]}
        return self._make_request(path, method="POST", body=body, needs_access_token=True)

    def upload_image(self, image_url):
        """Implements v2.media_space.upload_image"""
        path = "/media_space/upload_image"
        body = {"image_url": image_url}
        return self._make_request(path, method="POST", body=body, needs_access_token=True)

    # Placeholders for next steps
    def create_global_item(self, product_data, image_ids):
        print("\n[ShopeeClient] Creating global item...")
        return None

    def publish_item(self, global_item_id, shop_id):
        print(f"\n[ShopeeClient] Publishing item {global_item_id} for shop {shop_id}...")
        return None
