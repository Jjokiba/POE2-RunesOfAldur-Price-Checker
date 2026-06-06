import streamlit as st
import time
import tempfile
import os
from io import BytesIO
from PIL import Image
from ocr import read_image
from parser import parse_items
from trade_api import get_price, get_item_data
from output import print_results

# Set page config
st.set_page_config(
    page_title="POE2 Auto Search Value",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Title and description
st.title("💰 POE2 Auto Search Value")
st.markdown("""
This tool helps you quickly evaluate Runeshape valuations in the **Runes of Aldur** league.
Simply upload a screenshot of your items and get their market prices instantly!
""")

# File uploader
uploaded_file = st.file_uploader(
    "Upload your screenshot",
    type=["png", "jpg", "jpeg"],
    help="Upload a screenshot from your Path of Exile 2 inventory"
)

if uploaded_file is not None:
    # Create two columns
    left_col, right_col = st.columns([1, 1])
    
    with left_col:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Screenshot", use_container_width=True)
        
        # Process button
        search_button = st.button("🔍 Search Prices", type="primary", use_container_width=True)
    
    if search_button:
        try:
            with st.spinner("🎯 Extracting items from image..."):
                # Save temp image and read it
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                    temp_path = tmp_file.name
                    image.save(temp_path)
                
                raw_text = read_image(temp_path)
                
                # Clean up temp file
                os.unlink(temp_path)
            
            with st.spinner("✂️ Parsing items..."):
                items = parse_items(raw_text)
            
            if not items:
                st.error("❌ No items found in the screenshot. Please check the image and try again.")
            else:
                with right_col:
                    st.success(f"✅ Found {len(items)} items!")
                    
                    # Create console display container
                    with st.expander("📟 Live Console", expanded=False):
                        console_container = st.empty()
                
                # Fetch prices with progress
                prices = []
                currency_icons = []
                quantities = []
                with right_col:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                console_logs = []
                
                for idx, item in enumerate(items):
                    try:
                        status_text.text(f"📊 Fetching price for: **{item}**")
                        
                        try:
                            item_data = get_item_data(item)
                            price = item_data["price"]
                            currency_icon = item_data["currency_icon"]
                            quantity = item_data["quantity"]
                            
                            prices.append(price)
                            currency_icons.append(currency_icon)
                            quantities.append(quantity)
                            console_logs.append(f"✅ {item} | {price}")
                        except Exception as item_error:
                            prices.append("Error fetching")
                            currency_icons.append(None)
                            quantities.append(1)
                            console_logs.append(f"❌ {item} | Error: {str(item_error)}")
                    
                    except Exception as loop_error:
                        # Catch any unexpected errors in the loop
                        console_logs.append(f"❌ Unexpected error: {str(loop_error)}")
                        prices.append("Unknown Error")
                        currency_icons.append(None)
                        quantities.append(1)
                    
                    finally:
                        # Update console in real-time
                        console_output = "\n".join(console_logs)
                        console_container.code(console_output, language=None)
                        
                        # Update progress
                        progress = (idx + 1) / len(items)
                        progress_bar.progress(progress)
                        
                        # Rate limiting
                        time.sleep(2.5)
                
                # Display results on right column
                with right_col:
                    st.subheader("📈 Results")
                    
                    # Create a sortable dataframe
                    import pandas as pd
                    results_df = pd.DataFrame({
                        "Item": items,
                        "Price": prices,
                        "CurrencyIcon": currency_icons,
                        "Quantity": quantities
                    })
                    
                    # Sort by price (attempt to extract number for sorting)
                    def extract_price_value(price_str):
                        try:
                            return float(price_str.split()[0])
                        except:
                            return float('inf')
                    results_df["_sort_key"] = results_df["Price"].apply(extract_price_value)
                    results_df = results_df.sort_values("_sort_key").drop("_sort_key", axis=1).reset_index(drop=True)
                    
                    # Display results as custom HTML table with currency icons
                    html_table = '<table style="width:100%; border-collapse: collapse;">'
                    html_table += '<tr style="border-bottom: 1px solid #ddd;"><th style="text-align: left; padding: 8px;">Item</th><th style="text-align: center; padding: 8px;">Price</th></tr>'
                    
                    for idx, row in results_df.iterrows():
                        item_name = row["Item"]
                        price = row["Price"]
                        currency_icon = row["CurrencyIcon"]
                        quantity = row["Quantity"]
                        
                        # Build item display with quantity x item_name
                        item_display = f'{quantity}x {item_name}'
                        
                        # Build price display with currency icon
                        if currency_icon:
                            price_display = f'<img src="{currency_icon}" style="width: 24px; height: 24px; margin-right: 4px; vertical-align: middle;" title="Price"> {price}'
                        else:
                            price_display = price
                        
                        html_table += f'<tr style="border-bottom: 1px solid #f0f0f0;"><td style="padding: 8px;">{item_display}</td><td style="text-align: center; padding: 8px; font-weight: bold;">{price_display}</td></tr>'
                    
                    html_table += '</table>'
                    st.markdown(html_table, unsafe_allow_html=True)
                    
                    # Download button
                    csv = pd.DataFrame({
                        "Item": items,
                        "Price": prices,
                        "Quantity": quantities
                    }).to_csv(index=False)
                    st.download_button(
                        label="📥 Download as CSV",
                        data=csv,
                        file_name="poe2_prices.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Make sure your `.env` file has the correct `POESESSID` cookie set.")

st.divider()
st.caption("⚠️ Remember: Make sure you have set your `POESESSID` in the `.env` file")
