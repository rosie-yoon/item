# auth_util.py: Shopee OAuth2.0 Authorization Utility

import time
import hmac
import hashlib
import rich

from config import SHOPEE_API_V2_URL, REDIRECT_URL
from platforms.shopee_client import ShopeeClient
from user_manager import load_users, save_users

def generate_auth_url(partner_id, partner_key):
    """Generates the authorization URL for a user to grant access."""
    timestamp = int(time.time())
    full_path = "/api/v2/shop/auth_partner"
    base_string = f"{partner_id}{full_path}{timestamp}"
    sign = hmac.new(partner_key.encode('utf-8'), base_string.encode('utf-8'), hashlib.sha256).hexdigest()
    
    url = f"{SHOPEE_API_V2_URL.rstrip('/')}{full_path}?partner_id={partner_id}&redirect={REDIRECT_URL}&timestamp={timestamp}&sign={sign}"
    return url

if __name__ == "__main__":
    rich.print("[bold green]--- Shopee Shop Authorization Utility ---[/bold green]")
    
    try:
        partner_id_input = int(input("Enter your Partner ID: "))
    except ValueError:
        rich.print("[bold red]Invalid Partner ID. It must be a number.[/bold red]")
        exit()
        
    partner_key_input = input("Enter your Partner Key: ")

    auth_url = generate_auth_url(partner_id_input, partner_key_input)
    rich.print("\n[bold yellow]Step 1: Authorize Application[/bold yellow]")
    rich.print("Please open this URL in a browser to authorize the application:")
    rich.print(f"[link={auth_url}]{auth_url}[/link]")
    rich.print("\nAfter authorization, you will be redirected. Paste the 'code' and 'shop_id' from the redirect URL below.")
    
    auth_code = input("\nEnter the authorization [bold cyan]code[/bold cyan]: ")
    try:
        shop_id_input = int(input("Enter the [bold cyan]shop_id[/bold cyan]: "))
    except ValueError:
        rich.print("[bold red]Invalid Shop ID. It must be a number.[/bold red]")
        exit()

    rich.print("\n[bold yellow]Step 2: Acquiring Access Token...[/bold yellow]")
    client = ShopeeClient(partner_id=partner_id_input, partner_key=partner_key_input)
    token_data = client.get_access_token(auth_code=auth_code, shop_id=shop_id_input)

    if not token_data or "access_token" not in token_data:
        rich.print("[bold red]Error: Failed to acquire access token.[/bold red]")
        rich.print("Please check your Partner ID, Key, and the provided auth code/shop_id.")
        exit()

    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]
    rich.print("[bold green]Successfully acquired access token![/bold green]")

    rich.print("\n[bold yellow]Step 3: Fetching Shop Information...[/bold yellow]")
    # Re-initialize the client with the new token to make authorized calls
    authed_client = ShopeeClient(
        partner_id=partner_id_input,
        partner_key=partner_key_input,
        access_token=access_token,
        shop_id=shop_id_input
    )
    shop_info = authed_client.get_shop_info()
    
    if not shop_info or "shop_name" not in shop_info:
        rich.print("[bold red]Error: Failed to fetch shop information after getting token.[/bold red]")
        rich.print("The token might be invalid or the API service could be down. Please try again.")
        exit()
        
    shop_name = shop_info["shop_name"]
    rich.print(f"Successfully fetched info for shop: [bold cyan]{shop_name}[/bold cyan]")

    rich.print("\n[bold yellow]Step 4: Saving Profile[/bold yellow]")
    username = input("Enter a local username for this profile (e.g., 'my_sg_shop'): ")
    hosting_url = input(f"Enter the image hosting URL for {username} (e.g., https://unisiashop.com/): ")

    users = load_users()
    users[username] = {
        "partner_id": partner_id_input,
        "partner_key": partner_key_input,
        "shop_id": shop_id_input,
        "shop_name": shop_name,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "hosting_url": hosting_url.rstrip('/') # Ensure no trailing slash
    }
    
    save_users(users)
    rich.print(f"\n[bold green]Success![/bold green] Profile [bold cyan]'{username}'[/bold cyan] has been saved to [bold]users.json[/bold].")
