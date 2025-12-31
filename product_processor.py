# product_processor.py: Core logic for processing products.

import rich

def _prepare_cloned_product_data(source_data, new_image_id):
    """Prepares the payload for the new product, using data from the source and the new image."""
    
    # Replace the cover image and keep the rest
    original_image_ids = source_data.get("image", {}).get("image_id_list", [])
    new_image_ids = [new_image_id]
    if len(original_image_ids) > 1:
        new_image_ids.extend(original_image_ids[1:])

    # Construct the payload for the add_item API call
    # Note: This copies only the necessary and safe fields.
    # Some fields like `complaint_policy` or complex objects might require more specific handling.
    new_item_data = {
        "original_price": source_data.get("price_info")[0].get("original_price"),
        "description": source_data.get("description"),
        "item_name": source_data.get("item_name"),
        "item_sku": source_data.get("item_sku"), # Retain the parent SKU
        "category_id": source_data.get("category_id"),
        "image": {
            "image_id_list": new_image_ids
        },
        "stock_info_v2": source_data.get("stock_info_v2"),
        "logistic_info": source_data.get("logistic_info"),
        "attribute_list": source_data.get("attribute_list", []),
        "weight": source_data.get("weight", ""),
        "dimension": source_data.get("dimension", {})
    }
    
    # Return only non-null values to avoid API errors
    return {k: v for k, v in new_item_data.items() if v is not None}

def clone_single_product(platform_client, source_item_id, image_hosting_url, shop_code_for_image):
    """Clones a single product by fetching, modifying, and re-uploading."""
    
    # --- Step 1: Get Source Product Details ---
    rich.print(f"\n[bold yellow]Step 1: Fetching details for source product ID: {source_item_id}...[/bold yellow]")
    product_details_response = platform_client.get_product_details(source_item_id)
    if not product_details_response or not product_details_response.get("response") or not product_details_response["response"].get("item_list"):
        rich.print("[bold red]Error:[/bold red] Failed to fetch product details or the product does not exist.")
        return
    source_product_data = product_details_response["response"]["item_list"][0]
    rich.print("  ✓ Fetched product details successfully.")

    # --- Step 2: Construct New Image URL ---
    rich.print("\n[bold yellow]Step 2: Constructing new image URL...[/bold yellow]")
    parent_sku = source_product_data.get("item_sku")
    if not parent_sku:
        rich.print("[bold red]Error:[/bold red] Source product does not have an Item SKU (Parent SKU). Cannot generate image URL.")
        return
    new_cover_url = f"{image_hosting_url}/{parent_sku}_C_{shop_code_for_image}.jpg"
    rich.print(f"  ✓ Constructed new cover image URL: [link={new_cover_url}]{new_cover_url}[/link]")

    # --- Step 3: Upload New Cover Image ---
    rich.print("\n[bold yellow]Step 3: Uploading new cover image...[/bold yellow]")
    upload_response = platform_client.upload_image(new_cover_url)
    if not upload_response or not upload_response.get("response") or not upload_response["response"].get("image_info"):
        rich.print("[bold red]Error:[/bold red] Failed to upload the new image. Check if the image exists at the URL and is accessible.")
        return
    new_image_id = upload_response["response"]["image_info"]["image_id"]
    rich.print(f"  ✓ Image uploaded successfully. New Image ID: [bold cyan]{new_image_id}[/bold cyan]")

    # --- Step 4: Create New Product ---
    rich.print("\n[bold yellow]Step 4: Creating new product...[/bold yellow]")
    cloned_item_data = _prepare_cloned_product_data(source_product_data, new_image_id)
    create_response = platform_client.create_item(cloned_item_data)
    if not create_response or not create_response.get("response") or not create_response["response"].get("item_id"):
        rich.print("[bold red]Error:[/bold red] Failed to create the new product.")
        return
    new_item_id = create_response["response"]["item_id"]
    rich.print(f"  ✓ New product created successfully. New Item ID: [bold cyan]{new_item_id}[/bold cyan]")

    # --- Step 5: Publish New Product ---
    rich.print("\n[bold yellow]Step 5: Publishing new product...[/bold yellow]")
    publish_response = platform_client.publish_item(new_item_id)
    if not publish_response or not publish_response.get("response") or not publish_response["response"].get("item_id"):
        rich.print("[bold red]Error:[/bold red] Failed to publish the new product.")
        return
    
    published_item_id = publish_response["response"]["item_id"]
    rich.print(f"  ✓ Product [bold cyan]{published_item_id}[/bold cyan] published successfully!")
    rich.print("\n[bold green]🎉 Product cloning process completed! 🎉[/bold green]")
