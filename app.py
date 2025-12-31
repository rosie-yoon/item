
import streamlit as st
import json
from pathlib import Path
import sys
import io
import contextlib

# Add the project root to the Python path to allow imports from other modules
sys.path.append(str(Path(__file__).parent))

from platforms.shopee_client import ShopeeClient
from product_processor import clone_single_product
from config import SHOPEE_PARTNER_ID, SHOPEE_PARTNER_KEY

# --- Helper Functions ---

def load_profiles():
    """Loads shop profiles from the users.json file."""
    users_file = Path("users.json")
    if not users_file.exists():
        return {}
    with open(users_file, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

# --- Streamlit UI ---

st.set_page_config(page_title="Shopee Product Cloner", layout="wide")
st.title("🚀 Shopee Product Cloner")

st.info("This tool clones a Shopee product, replacing its cover image based on a naming convention.")

# --- Profile Selection ---
profiles = load_profiles()

if not profiles:
    st.error(
        "**No shop profiles found!** Please run `auth_util.py` in your terminal first to register a shop.",
        icon="🚨"
    )
    st.code("python auth_util.py", language="bash")
    st.stop()

profile_names = list(profiles.keys())
selected_profile_name = st.selectbox(
    "**Step 1: Select your Shop Profile**",
    profile_names,
    help="Choose the shop you want to clone the product into. Profiles are created by running `auth_util.py`."
)

# --- Product Input ---
st.markdown("---বাস")
st.subheader("**Step 2: Provide Product Details**")

col1, col2 = st.columns(2)

with col1:
    source_item_id_str = st.text_input(
        "Source Product ID",
        help="Enter the numerical ID of the product you wish to clone (e.g., '123456789')."
    )

with col2:
    shop_code_for_image = st.text_input(
        "Shop Code for New Image",
        help="Enter the shop code (e.g., 'SGM') used to generate the new cover image URL."
    )


# --- Execution ---
st.markdown("---বাস")
st.subheader("**Step 3: Run the Cloner**")

if st.button("✨ Clone Product", type="primary", use_container_width=True):
    if not source_item_id_str or not shop_code_for_image:
        st.warning("Please provide both a Source Product ID and a Shop Code before starting.", icon="⚠️")
    elif not source_item_id_str.isdigit():
        st.error("The Product ID must be a number.", icon="❌")
    else:
        source_item_id = int(source_item_id_str)
        selected_profile = profiles[selected_profile_name]

        # Prepare client
        client = ShopeeClient(
            partner_id=int(SHOPEE_PARTNER_ID),
            partner_key=SHOPEE_PARTNER_KEY,
            access_token=selected_profile["access_token"],
            shop_id=int(selected_profile["shop_id"])
        )

        st.info(f"Starting the cloning process for Product ID: {source_item_id}...", icon="⏳")
        
        log_placeholder = st.empty()
        log_placeholder.text("Logs will appear here...")

        try:
            # Redirect stdout to a string buffer to capture logs
            log_stream = io.StringIO()
            with contextlib.redirect_stdout(log_stream):
                clone_single_product(
                    platform_client=client,
                    source_item_id=source_item_id,
                    image_hosting_url=selected_profile["image_hosting_url"],
                    shop_code_for_image=shop_code_for_image
                )
            
            # Display the captured logs
            log_output = log_stream.getvalue()
            log_placeholder.code(log_output, language="log")

            if "🎉 Product cloning process completed! 🎉" in log_output:
                st.success("Cloning process completed successfully!", icon="✅")
            else:
                st.error("The process finished, but an error may have occurred. Please check the logs above.", icon="❌")

        except Exception as e:
            st.error(f"An unexpected error occurred during the process: {e}")
            st.exception(e)

