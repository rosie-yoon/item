# platforms/base_platform.py: Abstract interface for all platform clients

from abc import ABC, abstractmethod

class BasePlatform(ABC):
    """
    Defines the standard methods that every platform client must implement.
    This ensures that the product_processor can work with any platform.
    """
    
    @abstractmethod
    def get_product_details(self, item_id):
        pass
        
    @abstractmethod
    def upload_image(self, image_url):
        pass
        
    @abstractmethod
    def create_global_item(self, product_data, image_ids):
        pass
        
    @abstractmethod
    def publish_item(self, global_item_id, shop_id):
        pass

    @abstractmethod
    def get_access_token(self, auth_code, shop_id):
        pass
