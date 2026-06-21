import streamlit as st
import requests
import os
import base64
import pandas as pd
import random
from PIL import Image
import io
from streamlit_cropper import st_cropper

# Set professional page config
st.set_page_config(page_title="Visual Fashion Search Engine", layout="wide")

# Persistent Session Memory for Search, Filters, Shopping Cart, and Auth
if 'searched' not in st.session_state:
    st.session_state.searched = False
if 'raw_results' not in st.session_state:
    st.session_state.raw_results = []
if 'last_file' not in st.session_state:
    st.session_state.last_file = None
if 'cart' not in st.session_state:
    st.session_state.cart = {}
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'checkout_success' not in st.session_state:
    st.session_state.checkout_success = False

# Paths Configuration
CSV_PATH = "Fashion Dataset.csv"
DATASET_DIR = "dataset"

if not os.path.exists(DATASET_DIR):
    os.makedirs(DATASET_DIR)

# Smart CSV Database Loader
def load_dataset():
    if os.path.exists(CSV_PATH):
        try:
            df_temp = pd.read_csv(CSV_PATH)
            col_mapping = {col: col.lower().strip() for col in df_temp.columns}
            df_temp.rename(columns=col_mapping, inplace=True)
            
            target_col = None
            for potential_col in ['filename', 'file name', 'image', 'image_path', 'image_name']:
                if potential_col in df_temp.columns:
                    target_col = potential_col
                    break
                    
            if target_col:
                df_temp[target_col] = df_temp[target_col].astype(str).apply(lambda x: os.path.basename(x).strip().lower() if pd.notna(x) else "")
                return df_temp
            else:
                df_temp.iloc[:, 0] = df_temp.iloc[:, 0].astype(str).apply(lambda x: os.path.basename(x).strip().lower() if pd.notna(x) else "")
                df_temp.set_index(df_temp.columns[0], inplace=True)
                return df_temp
        except Exception as e:
            return None
    return None

df_products = load_dataset()

# BACKEND URLS
BACKEND_SEARCH_URL = "http://127.0.0.1:8000/search"
BACKEND_UPLOAD_URL = "http://127.0.0.1:8000/upload"

# ULTRA MODERN STREAMLIT CSS STYLING
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(90deg, rgba(15,17,21,0.95) 45%, rgba(15,17,21,0.6) 100%), 
                    url('https://images.unsplash.com/photo-1483985988355-763728e1935b?q=80&w=1600&auto=format&fit=crop');
        background-size: cover;
        background-position: right center;
        background-attachment: fixed;
    }
    h1 {
        color: #FFFFFF !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-top: 10px !important;
        margin-bottom: 2px !important;
    }
    .luxury-tagline {
        color: #00D2C4;
        font-weight: 600;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 12px;
    }
    .sub-title {
        color: #B2B9C9;
        font-size: 15px;
        margin-bottom: 25px;
        line-height: 1.5;
    }
    .stFileUploader {
        background: rgba(26, 29, 36, 0.65) !important;
        border: 2px dashed rgba(0, 210, 196, 0.3) !important;
        border-radius: 14px !important;
        padding: 10px !important;
    }
    
    .modern-section-heading {
        color: #FFFFFF !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 700;
        font-size: 20px !important;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 18px !important;
        border-left: 3px solid #00D2C4;
        padding-left: 10px;
        line-height: 1.2;
    }

    .admin-modern-heading {
        color: #FFFFFF !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 600;
        font-size: 16px !important;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-bottom: 15px !important;
        color: #00D2C4 !important;
        border-bottom: 1px solid rgba(0, 210, 196, 0.2);
        padding-bottom: 6px;
    }
    
    div.search-wrapper div[data-testid="stButton"] button {
        background: rgba(0, 210, 196, 0.04) !important;
        color: #00D2C4 !important;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        border: 1px solid #00D2C4 !important;
        border-radius: 30px !important;
        width: 100% !important;
        height: 44px !important;
        padding: 0px 20px !important;
        box-shadow: 0 0 12px rgba(0, 210, 196, 0.15) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }
    
    div.search-wrapper div[data-testid="stButton"] button:hover {
        background: #00D2C4 !important;
        color: #0A0C10 !important;
        border: 1px solid #00D2C4 !important;
        box-shadow: 0 0 25px rgba(0, 210, 196, 0.5) !important;
        transform: translateY(-1.5px) !important;
    }
    
    div.cart-btn-wrapper button {
        background: rgba(0, 0, 0, 0.4) !important;
        color: #00D2C4 !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        border-radius: 20px !important;
        border: 1px solid rgba(0, 210, 196, 0.5) !important;
        width: 100% !important;
    }
    
    div.checkout-wrapper button { background: #10B981 !important; color: white !important; width: 100% !important; }
    div.clear-wrapper button { background: #EF4444 !important; color: white !important; width: 100% !important; }
    
    div.admin-btn-wrapper button {
        background: linear-gradient(135deg, #00D2C4 0%, #00F2FE 100%) !important;
        color: #000000 !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        width: 100% !important;
    }

    .login-box {
        background: rgba(22, 25, 32, 0.95);
        padding: 30px;
        border-radius: 16px;
        border: 1px solid rgba(0, 210, 196, 0.25);
        text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.5);
    }
    
    [data-testid="stVerticalBlockBorderContainer"] {
        background: rgba(22, 25, 32, 0.75) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 14px !important;
        padding: 15px !important;
    }

    [data-testid="stSidebar"] { background-color: #111318 !important; }

    [data-testid="stImage"] img {
        display: block !important;
        margin-left: auto !important;
        margin-right: auto !important;
        width: auto !important;
        max-width: 100% !important;
        height: 150px !important;
        object-fit: contain !important;
        border-radius: 8px !important;
    }

    [data-testid="stImage"] {
        height: 150px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }

    .badge-container {
        height: 25px;
        display: flex;
        align-items: center;
        margin-bottom: 5px;
    }

    .gauge-track {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 4px;
        height: 5px;
        width: 100%;
        margin: 4px 0 10px 0;
        overflow: hidden;
    }
    .gauge-fill {
        background: linear-gradient(90deg, #00D2C4, #00F2FE);
        height: 100%;
        border-radius: 4px;
        box-shadow: 0 0 8px rgba(0, 242, 254, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# ==================== NAVIGATION CONTROL ====================
st.sidebar.markdown("<h2>👤 System View Mode</h2>", unsafe_allow_html=True)
view_mode = st.sidebar.selectbox("Choose Mode", ["🛍️ Customer Store", "⚙️ Admin Dashboard"])
st.sidebar.markdown("---")

# ==================== 1. CUSTOMER STORE VIEW ====================
if view_mode == "🛍️ Customer Store":
    st.markdown("<h1>Smart Visual Fashion Finder</h1>", unsafe_allow_html=True)
    st.markdown("<div class='luxury-tagline'>• Powered by Next-Gen AI</div>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Can't find the words to describe a style? Simply upload a picture, crop the exact area, and our AI will instantly scan our catalog.</p>", unsafe_allow_html=True)

    # SIDEBAR CART SYSTEM
    st.sidebar.markdown("### 🛒 Your Shopping Cart")
    
    # Persistent Checkout Success Display Area
    if st.session_state.checkout_success:
        st.sidebar.success("✅ Order placed successfully!")
        if st.sidebar.button("Dismiss Message", key="dismiss_msg"):
            st.session_state.checkout_success = False
            st.rerun()
        st.sidebar.markdown("---")

    if st.session_state.cart:
        st.session_state.checkout_success = False # reset state if items exist
        
        total_bill = 0
        for p_id, item_info in list(st.session_state.cart.items()):
            sub_total = item_info['price'] * item_info['qty']
            total_bill += sub_total
            st.sidebar.markdown(f"**Item #{p_id}** ({item_info['qty']}x) - LKR {sub_total:,}")
        st.sidebar.markdown(f"Total: LKR {total_bill:,}")
        
        col_cart1, col_cart2 = st.sidebar.columns(2)
        with col_cart1:
            st.markdown('<div class="checkout-wrapper">', unsafe_allow_html=True)
            if st.button("Checkout"):
                if os.path.exists(CSV_PATH):
                    try:
                        df_db = pd.read_csv(CSV_PATH)
                        # Standardize columns to lowercase and trim spaces
                        df_db.columns = [c.strip().lower() for c in df_db.columns]
                        
                        # Find title column
                        fn_idx = 0
                        for target in ['title', 'name', 'product_name', 'filename', 'file name']:
                            if target in df_db.columns:
                                fn_idx = df_db.columns.get_loc(target)
                                break
                        actual_fn_col = df_db.columns[fn_idx]
                        
                        # ADVANCED BUG FIX: Find the stock column properly including 'stock_count'
                        actual_stock_col = None
                        for c in df_db.columns:
                            if 'stock' in c or 'qty' in c or 'quantity' in c or 'avail' in c or 'count' in c:
                                actual_stock_col = c
                                break
                        
                        if actual_stock_col is None:
                            st.sidebar.error("Stock column not found in CSV! Adding a default 'stock_count' column.")
                            df_db['stock_count'] = 10
                            actual_stock_col = 'stock_count'
                            
                        # Update stock data safely
                        for cart_id, cart_info in list(st.session_state.cart.items()):
                            matched = df_db[df_db[actual_fn_col].astype(str).str.strip().str.lower().str.contains(str(cart_id).strip().lower(), na=False) |
                                            df_db[actual_fn_col].astype(str).str.strip().str.lower().eq(str(cart_id).strip().lower())]
                            
                            if not matched.empty:
                                for idx in matched.index:
                                    try:
                                        current_st = int(float(df_db.at[idx, actual_stock_col]))
                                        df_db.at[idx, actual_stock_col] = max(0, current_st - cart_info['qty'])
                                    except:
                                        df_db.at[idx, actual_stock_col] = max(0, 10 - cart_info['qty'])
                        
                        df_db.to_csv(CSV_PATH, index=False)
                        
                        if st.session_state.raw_results:
                            for item in st.session_state.raw_results:
                                item_id = str(item['product_name']).strip()
                                if item_id in st.session_state.cart:
                                    purchased_qty = st.session_state.cart[item_id]['qty']
                                    item['stock_count'] = max(0, item['stock_count'] - purchased_qty)
                        
                        # STABLE REFRESH RESOLUTION
                        st.session_state.cart = {}
                        st.session_state.checkout_success = True  
                        st.rerun()
                    except Exception as e:
                        st.sidebar.error(f"Execution failed: {e}")
                else:
                    st.sidebar.error(f"❌ '{CSV_PATH}' file not found!")
            st.markdown('</div>', unsafe_allow_html=True)
        with col_cart2:
            st.markdown('<div class="clear-wrapper">', unsafe_allow_html=True)
            if st.button("Clear"):
                st.session_state.cart = {}
                st.session_state.checkout_success = False
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        if not st.session_state.checkout_success:
            st.sidebar.info("Your cart is empty.")

    st.sidebar.markdown("---")

    # SIDEBAR FILTERS
    st.sidebar.markdown("### ⚙️ Store Filters")
    category_filter = st.sidebar.selectbox("Category", ["All Categories", "T-shirt", "Jeans", "Frock", "Shirts", "Jackets"])
    size_filter = st.sidebar.selectbox("Available Size", ["All Sizes", "S", "M", "L", "XL", "XXL"])
    price_range = st.sidebar.slider("💵 Price Range (LKR)", 500, 15000, (500, 15000), step=500)
    sort_option = st.sidebar.radio("🔀 Sort Results By", ["AI Match Score (Highest)", "Price: Low to High", "Price: High to Low"])

    # MAIN PANEL INTERFACE
    layout_left, layout_center, layout_right = st.columns([0.1, 3.8, 0.1])

    with layout_center:
        input_tab1, input_tab2 = st.tabs(["📤 Upload & Crop Image", "📸 Live AI Camera"])
        active_image_bytes, active_image_name, active_image_type = None, None, "image/jpeg"
        
        with input_tab1:
            col_upload, col_cropper = st.columns([2, 1.8], gap="large")
            with col_upload:
                st.markdown("<p style='color:#FFF; font-size:14px; font-weight:600;'>Drop or Select your file:</p>", unsafe_allow_html=True)
                uploaded_file = st.file_uploader("Choose a fashion image...", type=["jpg", "jpeg", "png", "webp"], label_visibility="collapsed")
            
            search_clicked_file = False
            if uploaded_file is not None:
                img = Image.open(uploaded_file)
                
                max_preview_width = 200
                if img.width > max_preview_width:
                    ratio = max_preview_width / float(img.width)
                    new_height = int(float(img.height) * float(ratio))
                    img = img.resize((max_preview_width, new_height), Image.Resampling.LANCZOS)
                
                with col_cropper:
                    st.markdown("<p style='color:#00D2C4; font-size:13px; font-weight:600; margin-bottom: 8px;'>✂️ Drag corners to crop target garment:</p>", unsafe_allow_html=True)
                    cropped_img = st_cropper(img, realtime_update=True, box_color='#00D2C4', aspect_ratio=None)
                    
                    img_byte_arr = io.BytesIO()
                    cropped_img.save(img_byte_arr, format='JPEG')
                    active_image_bytes = img_byte_arr.getvalue()
                    active_image_name = uploaded_file.name
                    
                    st.markdown('<div class="search-wrapper" style="margin-top: 2px;">', unsafe_allow_html=True)
                    search_clicked_file = st.button("Search Focused Style", key="file_search_btn")
                    st.markdown('</div>', unsafe_allow_html=True)

        with input_tab2:
            camera_file = st.camera_input("Take a photo of the outfit", label_visibility="collapsed")
            st.markdown('<div class="search-wrapper" style="margin-top: 10px;">', unsafe_allow_html=True)
            search_clicked_camera = st.button("Scan Live Camera Photo", key="camera_search_btn")
            st.markdown('</div>', unsafe_allow_html=True)
            
            if camera_file is not None:
                active_image_bytes = camera_file.getvalue()
                active_image_name = "live_capture.jpg"

    search_triggered = search_clicked_camera if active_image_name == "live_capture.jpg" else search_clicked_file

    if active_image_bytes is None:
        st.session_state.searched = False
        st.session_state.raw_results = []

    # API SEARCH OPERATION
    if active_image_bytes is not None and search_triggered:
        with st.spinner("Our AI Stylist is searching the boutique..."):
            try:
                files = {"file": (active_image_name, active_image_bytes, "image/jpeg")}
                response = requests.post(BACKEND_SEARCH_URL, files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        raw_api_results = data.get("results", [])
                        processed_results = []
                        
                        df_products = load_dataset()
                        
                        for item in raw_api_results:
                            img_file_name = os.path.basename(item["filename"]).strip().lower()
                            try: ai_score = float(item.get("score", 0.0))
                            except: ai_score = 0.0
                            
                            item_cat = "T-shirt"
                            item_price = random.choice([1800, 2900, 3400, 4200, 5500, 6800, 8500])
                            item_sizes = ["S", "M", "L", "XL"]
                            prod_title = os.path.splitext(img_file_name)[0].replace("_", " ").strip()
                            item_stock = 10 
                            
                            if df_products is not None:
                                if 'filename' in df_products.columns:
                                    search_df = df_products.set_index('filename')
                                else:
                                    search_df = df_products
                                    
                                if img_file_name in search_df.index:
                                    db_row = search_df.loc[img_file_name]
                                    if isinstance(db_row, pd.DataFrame): db_row = db_row.iloc[0]
                                        
                                    for col in db_row.index:
                                        if 'cat' in str(col): item_cat = str(db_row[col]).strip()
                                        elif 'price' in str(col):
                                            try: item_price = int(float(db_row[col]))
                                            except: pass
                                        elif 'size' in str(col): item_sizes = [s.strip() for s in str(db_row[col]).split(",")]
                                        elif 'name' in str(col) or 'title' in str(col): prod_title = str(db_row[col]).strip()
                                        elif 'stock' in str(col) or 'qty' in str(col) or 'quantity' in str(col) or 'avail' in str(col) or 'count' in str(col):
                                            try: item_stock = int(float(db_row[col]))
                                            except: item_stock = 10
                            
                            processed_results.append({
                                "filename": item["filename"], "score": ai_score, "product_name": prod_title,
                                "category": item_cat, "price": item_price, "sizes": item_sizes, "stock_count": item_stock
                            })
                        st.session_state.raw_results = processed_results
                        st.session_state.searched = True
            except Exception as e:
                st.error(f"Connection Failed: {e}")

    # RESULTS MATRIX
    if active_image_bytes is not None and st.session_state.searched and st.session_state.raw_results:
        st.markdown("---")
        col1, col2 = st.columns([1, 2.5], gap="large")
        with col1:
            st.markdown("<p class='modern-section-heading'>Focused Crop Area</p>", unsafe_allow_html=True)
            base64_image = base64.b64encode(active_image_bytes).decode()
            st.markdown(f'<img src="data:image/jpeg;base64,{base64_image}" style="width:200px; border-radius:14px; display:block; margin:0 auto;" />', unsafe_allow_html=True)
            
        with col2:
            st.markdown("<p class='modern-section-heading'>Best AI Inventory Matches</p>", unsafe_allow_html=True)
            filtered_list = []
            for item in st.session_state.raw_results:
                if category_filter != "All Categories" and item["category"].lower() != category_filter.lower(): continue
                if size_filter != "All Sizes" and size_filter not in item["sizes"]: continue
                if not (int(price_range[0]) <= int(item["price"]) <= int(price_range[1])): continue
                filtered_list.append(item)
                
            if sort_option == "Price: Low to High": filtered_list.sort(key=lambda x: int(x["price"]))
            elif sort_option == "Price: High to Low": filtered_list.sort(key=lambda x: int(x["price"]), reverse=True)
            else: filtered_list.sort(key=lambda x: float(x["score"]), reverse=True)

            if filtered_list:
                with st.container(border=False):
                    grid_cols = st.columns(3, gap="medium")
                    for idx, item in enumerate(filtered_list):
                        with grid_cols[idx % 3]:
                            exact_img_path = os.path.join(DATASET_DIR, os.path.basename(item["filename"]))
                            match_p = round(item["score"] * 100, 1)
                            st_count = item.get("stock_count", 10)
                            
                            with st.container(border=True):
                                st.markdown('<div class="badge-container">', unsafe_allow_html=True)
                                if st_count <= 0:
                                    st.markdown("<p style='color:#CBD5E0; background:#4A5568; font-size:11px; font-weight:bold; padding:3px 8px; border-radius:10px; margin:0;'>🚫 Out of Stock</p>", unsafe_allow_html=True)
                                elif 0 < st_count <= 4:
                                    st.markdown(f"<p style='color:white; background:linear-gradient(135deg, #FF0844 0%, #FFB199 100%); font-size:11px; font-weight:bold; padding:3px 8px; border-radius:10px; margin:0;'>🔥 Only {st_count} left!</p>", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"<p style='color:#00D2C4; background:rgba(0,210,196,0.1); font-size:11px; font-weight:bold; padding:3px 8px; border-radius:10px; margin:0;'>📦 Stock: {st_count}</p>", unsafe_allow_html=True)
                                st.markdown('</div>', unsafe_allow_html=True)

                                if os.path.exists(exact_img_path):
                                    st.image(exact_img_path, use_container_width=True)
                                else:
                                    st.image("https://placehold.co/200x200?text=No+Image", use_container_width=True)
                                    
                                st.markdown(f"""
                                <p style='color:#FFF; font-weight:bold; margin:8px 0 2px 0; font-size:14px; text-overflow:ellipsis; overflow:hidden; white-space:nowrap;'>{item['product_name']}</p>
                                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:0px;'>
                                    <span style='color:#00D2C4; font-weight:600; font-size:12px;'>AI Match</span>
                                    <span style='color:#00F2FE; font-weight:bold; font-size:12px;'>{match_p}%</span>
                                </div>
                                <div class="gauge-track">
                                    <div class="gauge-fill" style="width: {match_p}%;"></div>
                                </div>
                                <h4 style='color:#FFF; margin:4px 0;'>LKR {item['price']:,}</h4>
                                """, unsafe_allow_html=True)
                                
                                st.markdown('<div class="cart-btn-wrapper">', unsafe_allow_html=True)
                                if st_count <= 0:
                                    st.button("🚫 Sold Out", key=f"add_{idx}", disabled=True, use_container_width=True)
                                else:
                                    if st.button("➕ Add to Cart", key=f"add_{idx}", use_container_width=True):
                                        p_id_clean = str(item['product_name']).strip()
                                        if p_id_clean in st.session_state.cart: 
                                            if st.session_state.cart[p_id_clean]['qty'] < st_count:
                                                st.session_state.cart[p_id_clean]['qty'] += 1
                                                st.toast(f"Updated qty for #{p_id_clean}!")
                                            else:
                                                st.error(f"Cannot add more! Only {st_count} available.")
                                        else: 
                                            st.session_state.cart[p_id_clean] = {"price": item['price'], "qty": 1}
                                            st.toast(f"Added #{p_id_clean} to cart!")
                                        st.session_state.checkout_success = False
                                        st.rerun()
                                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No items match your criteria.")

# ==================== 2. ADMIN DASHBOARD VIEW ====================
elif view_mode == "⚙️ Admin Dashboard":
    st.markdown("<h1>⚙️ Merchant Inventory Control</h1>", unsafe_allow_html=True)
    st.markdown("<div class='luxury-tagline'>🔒 Admin Secure Portal</div>", unsafe_allow_html=True)
    
    if not st.session_state.authenticated:
        _, center_col, _ = st.columns([1, 1.5, 1])
        with center_col:
            st.markdown("""
            <div class='login-box'>
                <h3 style='color: #FFF; margin:0 0 10px 0;'>🔒 Identity Verification</h3>
                <p style='color: #A0AEC0; font-size:14px;'>Please enter your merchant authentication PIN.</p>
            """, unsafe_allow_html=True)
            password = st.text_input("PIN Input Field", type="password", label_visibility="collapsed")
            st.markdown("</div>", unsafe_allow_html=True)
            
            if password == "admin123":
                st.session_state.authenticated = True
                st.rerun()
            elif password != "":
                st.error("Incorrect PIN.")
    
    if st.session_state.authenticated:
        st.success("🔓 Access Granted!")
        admin_tab1, admin_tab2 = st.tabs(["➕ Add New Product", "📝 Edit & Delete Existing Product"])
        
        with admin_tab1:
            adm_col1, adm_col2 = st.columns([1.5, 2], gap="large")
            with adm_col1:
                st.markdown("<p class='admin-modern-heading'>Upload Garment Photo</p>", unsafe_allow_html=True)
                new_img_file = st.file_uploader("Choose Product Image", type=["jpg", "jpeg", "png", "webp"], key="add_uploader")
                if new_img_file: st.image(new_img_file, width=220)
                    
            with adm_col2:
                st.markdown("<p class='admin-modern-heading'>Product Details</p>", unsafe_allow_html=True)
                new_title = st.text_input("Product Title / Name", key="add_title")
                new_cat = st.selectbox("Product Category", ["T-shirt", "Jeans", "Frock", "Shirts", "Jackets"], key="add_cat")
                
                p_s_col1, p_s_col2 = st.columns(2)
                new_price = p_s_col1.number_input("Retail Price (LKR)", min_value=100, value=2500, key="add_price")
                new_stock = p_s_col2.number_input("Stock Available Qty", min_value=0, value=15, key="add_stock")
                
                st.write("Available Sizes")
                size_cols = st.columns(5)
                s_s = size_cols[0].checkbox("S", value=True, key="add_s")
                s_m = size_cols[1].checkbox("M", value=True, key="add_m")
                s_l = size_cols[2].checkbox("L", value=True, key="add_l")
                s_xl = size_cols[3].checkbox("XL", key="add_xl")
                s_xxl = size_cols[4].checkbox("XXL", key="add_xxl")
                
                st.markdown('<div class="admin-btn-wrapper" style="margin-top:15px;">', unsafe_allow_html=True)
                submit_product = st.button("Add Product")
                st.markdown('</div>', unsafe_allow_html=True)
                
                if submit_product and new_img_file and new_title.strip():
                    try:
                        clean_filename = new_img_file.name.replace(" ", "_").lower()
                        with open(os.path.join(DATASET_DIR, clean_filename), "wb") as f:
                            f.write(new_img_file.getbuffer())
                        
                        selected_sizes = [sz for sz, active in [("S", s_s), ("M", s_m), ("L", s_l), ("XL", s_xl), ("XXL", s_xxl)] if active]
                        new_row_df = pd.DataFrame([{"filename": clean_filename, "category": new_cat, "price": int(new_price), "size": ", ".join(selected_sizes), "title": new_title.strip(), "stock_count": int(new_stock)}])
                        
                        if os.path.exists(CSV_PATH): new_row_df.to_csv(CSV_PATH, mode='a', header=False, index=False)
                        else: new_row_df.to_csv(CSV_PATH, index=False)
                            
                        requests.post(BACKEND_UPLOAD_URL, files={"file": (clean_filename, new_img_file.getvalue(), new_img_file.type)})
                        st.success("Product Saved and Indexed Successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to record data: {e}")
            
        with admin_tab2:
            try:
                df_edit = pd.read_csv(CSV_PATH)
                df_edit.columns = [c.lower().strip() for c in df_edit.columns]
            except:
                df_edit = None
                
            if df_edit is not None and not df_edit.empty:
                title_col = None
                for c in ['title', 'name', 'product_name']:
                    if c in df_edit.columns: title_col = c; break
                if not title_col: title_col = df_edit.columns[0]
                
                product_list = df_edit[title_col].dropna().unique().tolist()
                selected_edit_product = st.selectbox("🎯 Select Product to Edit", product_list)
                
                prod_row = df_edit[df_edit[title_col] == selected_edit_product].iloc[0]
                
                curr_filename = str(prod_row.get('filename', '')).strip()
                curr_cat = str(prod_row.get('category', 'T-shirt')).strip()
                try: curr_price = int(float(prod_row.get('price', 2500)))
                except: curr_price = 2500
                try: curr_stock = int(float(prod_row.get('stock_count', 10)))
                except: curr_stock = 10
                curr_sizes_str = str(prod_row.get('size', 'S, M, L'))
                
                st.markdown("---")
                edit_col1, edit_col2 = st.columns([1.5, 2], gap="large")
                
                with edit_col1:
                    st.markdown("<p class='admin-modern-heading'>Current Product Image</p>", unsafe_allow_html=True)
                    if curr_filename and any(curr_filename.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                        exact_img_path = os.path.join(DATASET_DIR, curr_filename)
                        if os.path.exists(exact_img_path) and os.path.isfile(exact_img_path):
                            st.image(exact_img_path, width=220)
                        else:
                            st.warning("⚠️ Original image file not found in dataset folder.")
                    else:
                        st.info("ℹ️ No unique valid image attached to this entry.")
                        
                with edit_col2:
                    st.markdown("<p class='admin-modern-heading'>Edit Product Information</p>", unsafe_allow_html=True)
                    edit_title = st.text_input("Product Title / Name", value=selected_edit_product)
                    
                    cat_list = ["T-shirt", "Jeans", "Frock", "Shirts", "Jackets"]
                    cat_index = cat_list.index(curr_cat) if curr_cat in cat_list else 0
                    edit_cat = st.selectbox("Product Category", cat_list, index=cat_index)
                    
                    e_p_s_col1, e_p_s_col2 = st.columns(2)
                    edit_price = e_p_s_col1.number_input("Retail Price (LKR)", min_value=100, value=curr_price, key="ed_price")
                    edit_stock = e_p_s_col2.number_input("Stock Available Qty", min_value=0, value=curr_stock, key="ed_stock")
                    
                    st.write("Available Sizes")
                    es_cols = st.columns(5)
                    es_s = es_cols[0].checkbox("S", value=("S" in curr_sizes_str), key="edit_s")
                    es_m = es_cols[1].checkbox("M", value=("M" in curr_sizes_str), key="edit_s_m")
                    es_l = es_cols[2].checkbox("L", value=("L" in curr_sizes_str), key="edit_s_l")
                    es_xl = es_cols[3].checkbox("XL", value=("XL" in curr_sizes_str), key="edit_s_xl")
                    es_xxl = es_cols[4].checkbox("XXL", value=("XXL" in curr_sizes_str), key="edit_s_xxl")
                    
                    st.markdown('<div class="admin-btn-wrapper" style="margin-top:15px;">', unsafe_allow_html=True)
                    
                    btn_col1, btn_col2 = st.columns(2)
                    update_clicked = btn_col1.button(" Update Changes")
                    delete_clicked = btn_col2.button("Delete Product", type="primary")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    if update_clicked:
                        try:
                            idx_to_update = df_edit[df_edit[title_col] == selected_edit_product].index[0]
                            selected_sizes = [sz for sz, active in [("S", es_s), ("M", es_m), ("L", es_l), ("XL", es_xl), ("XXL", es_xxl)] if active]
                            
                            df_edit.at[idx_to_update, title_col] = edit_title.strip()
                            df_edit.at[idx_to_update, 'category'] = edit_cat
                            df_edit.at[idx_to_update, 'price'] = int(edit_price)
                            df_edit.at[idx_to_update, 'stock_count'] = int(edit_stock)
                            df_edit.at[idx_to_update, 'size'] = ", ".join(selected_sizes)
                            
                            df_edit.to_csv(CSV_PATH, index=False)
                            st.success(f"Changes saved for '{edit_title}' successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to update CSV database: {e}")
                            
                    if delete_clicked:
                        try:
                            df_edit = df_edit[df_edit[title_col] != selected_edit_product]
                            df_edit.to_csv(CSV_PATH, index=False)
                            st.success(f"Product '{selected_edit_product}' deleted successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed to delete product: {e}")
            else:
                st.info("No items found in your database to edit yet.")
            