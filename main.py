# main.py: CLI Interface & Workflow Controller
import rich
from user_manager import load_users
from platforms.shopee_client import ShopeeClient
import product_processor

def select_user_profile():
    """Displays available user profiles and prompts the user to select one."""
    users = load_users()
    if not users:
        rich.print("[bold red]No user profiles found![/bold red]")
        rich.print("Please run [bold]python auth_util.py[/bold] first to register a shop.")
        return None

    rich.print("\n[bold]Available User Profiles:[/bold]")
    profile_list = list(users.items())
    for i, (username, data) in enumerate(profile_list):
        rich.print(f"  {i + 1}. [cyan]{username}[/cyan] (Shop: [yellow]{data['shop_name']}[/yellow])")

    while True:
        try:
            choice = int(input("\nSelect a profile to use: "))
            if 1 <= choice <= len(profile_list):
                selected_username, selected_profile = profile_list[choice - 1]
                rich.print(f"Using profile: [cyan]{selected_username}[/cyan]")
                return selected_profile
            else:
                rich.print("[yellow]Invalid selection. Please try again.[/yellow]")
        except ValueError:
            rich.print("[red]Invalid input. Please enter a number.[/red]")

def clone_product_flow():
    """Guides the user through the product cloning process based on new requirements."""
    selected_profile = select_user_profile()
    if not selected_profile:
        return

    rich.print(f"\nCloning products for shop: [bold yellow]{selected_profile['shop_name']}[/bold yellow]")

    try:
        source_item_id = int(input("Enter the source product ID to clone: "))
    except ValueError:
        rich.print("[bold red]Invalid Product ID. It must be a number.[/bold red]")
        return

    shop_code = input("Enter the ShopCode for the new cover image (e.g., ONE): ")

    # Initialize the platform client with the selected profile's credentials
    client = ShopeeClient(
        partner_id=selected_profile['partner_id'],
        partner_key=selected_profile['partner_key'],
        access_token=selected_profile['access_token'],
        shop_id=selected_profile['shop_id']
    )

    # Start the cloning process with the new arguments
    product_processor.clone_single_product(
        platform_client=client,
        source_item_id=source_item_id,
        image_hosting_url=selected_profile['hosting_url'],
        shop_code_for_image=shop_code
    )

def main_menu():
    rich.print("\n[bold green]Shopee Product Cloner v2.0[/bold green]")
    rich.print("1. [bold]Clone a single product[/bold]")
    rich.print("2. [bold]Register a new shop[/bold]")
    rich.print("3. [bold]Exit[/bold]")

    while True:
        try:
            choice = input("\nSelect an option: ")
            if choice == '1':
                clone_product_flow()
                break
            elif choice == '2':
                rich.print("\nPlease run [bold cyan]python auth_util.py[/bold cyan] from your terminal.")
                break
            elif choice == '3':
                rich.print("[yellow]Exiting...[/yellow]")
                break
            else:
                rich.print("[yellow]Invalid selection. Please try again.[/yellow]")
        except (ValueError, KeyboardInterrupt):
            rich.print("\n[yellow]Exiting...[/yellow]")
            break

if __name__ == "__main__":
    main_menu()
