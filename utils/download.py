import os
import json
import requests
from PIL import Image, ImageOps
from io import BytesIO
import concurrent.futures

def process_emoji(index, emoji):
    try:
        img_name = f'img{index + 1}.png'
        txt_name = f'img{index + 1}.txt'
        
        # Download image
        response = requests.get(emoji['link'])
        response.raise_for_status()  # Raise an error for bad responses
        img = Image.open(BytesIO(response.content))
        
        # Add white background
        img = ImageOps.expand(img, border=10, fill='white')
        
        # Save image
        img.save(f'./emojis/{img_name}')
        
        # Save processed name
        with open(f'./emojis/{txt_name}', 'w') as txt_file:
            txt_file.write(emoji['processed'])
        
        print(f'Finished processing {img_name}')
    except Exception as e:
        print(f'Error processing {emoji}: {e}')

# Load emoji data
with open('./emoji_data.json', 'r') as file:
    emoji_data = json.load(file)

# Create directory if it doesn't exist
os.makedirs('./emojis', exist_ok=True)

# Use multithreading to process emojis
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(process_emoji, index, emoji) for index, emoji in enumerate(emoji_data)]
    
    # Wait for all threads to complete
    concurrent.futures.wait(futures)

print('All images have been processed.')
