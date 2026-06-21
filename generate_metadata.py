import os
import csv
import random

DATASET_DIR = "dataset"
CSV_FILENAME = "Fashion Dataset.csv"

if not os.path.exists(DATASET_DIR):
    print(f"❌ Error: Directory '{DATASET_DIR}' not found!")
    exit()

image_files = [f for f in os.listdir(DATASET_DIR) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

print(f"📦 Found {len(image_files)} images. Generating CSV metadata file...")

with open(CSV_FILENAME, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["filename", "product_name", "category", "price", "sizes"])
    
    for idx, img_name in enumerate(image_files):
        name_lower = img_name.lower()
        
        # Rule-based auto category assignment based on filename
        if "jean" in name_lower or "pant" in name_lower or "denim" in name_lower:
            category = "Jeans"
            prod_name = f"Premium Denim Pant {idx}"
        elif "frock" in name_lower or "dress" in name_lower or "gown" in name_lower:
            category = "Frock"
            prod_name = f"Designer Fashion Frock {idx}"
        elif "shirt" in name_lower:
            category = "Shirts"
            prod_name = f"Casual Cotton Shirt {idx}"
        elif "jacket" in name_lower or "coat" in name_lower:
            category = "Jackets"
            prod_name = f"Modern Winter Jacket {idx}"
        else:
            category = "T-shirt"
            prod_name = f"Sleek Crewneck T-Shirt {idx}"
            
        # Generating dynamic prices bounded reasonably for the dataset
        price = random.randint(3, 17) * 500  # Generates prices from 1500 to 8500
        sizes = "S, M, L, XL"
        
        writer.writerow([img_name, prod_name, category, price, sizes])

print(f"✅ Success! Generated '{CSV_FILENAME}' for {len(image_files)} items. 🚀")