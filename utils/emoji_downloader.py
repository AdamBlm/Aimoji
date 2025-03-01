import os
import requests
import time
import random
from bs4 import BeautifulSoup
from PIL import Image, ImageOps
from io import BytesIO
import concurrent.futures

def download_emoji(emoji, index, total_count):
    """Download a single emoji"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://emojigraph.org/',
    }
    
    try:
        print(f"🔄 Processing {index+1}/{total_count}: {emoji['name']}")
        
        # Get the emoji page
        emoji_page = requests.get(emoji['url'], headers=headers)
        if emoji_page.status_code != 200:
            print(f"❌ Failed to access page for {emoji['name']}: {emoji_page.status_code}")
            return False
        
        # Parse emoji page
        emoji_soup = BeautifulSoup(emoji_page.content, "html.parser")
        
        # Try different selectors to find the image
        img_element = None
        selectors = [
            "img[alt*='emoji']",
            ".card img",
            ".container .row img",
            "img"  # Fallback to any image
        ]
        
        for selector in selectors:
            elements = emoji_soup.select(selector)
            if elements:
                # Try to find the most relevant image
                for elem in elements:
                    src = elem.get("src", "")
                    alt = elem.get("alt", "")
                    
                    # Check if this seems like a main emoji image
                    if src and (
                        "apple" in src.lower() or 
                        emoji['name'] in src.lower() or
                        (alt and emoji['name'] in alt.lower())
                    ):
                        img_element = elem
                        break
                
                # If found a candidate, stop trying selectors
                if img_element:
                    break
        
        # If still no image found, use the first image as a fallback
        if not img_element and emoji_soup.find("img"):
            img_element = emoji_soup.find("img")
        
        # Still no image? Exit with error
        if not img_element:
            print(f"❌ Could not find any image for {emoji['name']}")
            return False
        
        img_url = img_element.get("src")
        if not img_url:
            print(f"❌ Empty image URL for {emoji['name']}")
            return False
        
        # Make sure it's an absolute URL
        if not img_url.startswith("http"):
            img_url = "https://emojigraph.org" + (img_url if img_url.startswith("/") else "/" + img_url)
        
        # Download the image
        img_response = requests.get(img_url, headers=headers)
        if img_response.status_code != 200:
            print(f"❌ Failed to download image for {emoji['name']}: {img_response.status_code}")
            return False
        
        # Check if we got an image
        content_type = img_response.headers.get('Content-Type', '')
        if 'image' not in content_type:
            print(f"❌ Invalid content type for {emoji['name']}: {content_type}")
            return False
        
        # Save the image
        img_name = f'img{index + 1}.png'
        txt_name = f'img{index + 1}.txt'
        img_path = os.path.join('./emojis', img_name)
        txt_path = os.path.join('./emojis', txt_name)
        
        # Process image
        img = Image.open(BytesIO(img_response.content))
        img = ImageOps.expand(img, border=10, fill='white')
        
        # Save image
        img.save(img_path)
        
        # Save processed name
        with open(txt_path, 'w') as txt_file:
            txt_file.write(emoji['processed'])
        
        print(f"✅ Saved {emoji['name']} as {img_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {emoji['name']}: {str(e)}")
        return False

def main():
    # Create directory for emojis
    os.makedirs('./emojis', exist_ok=True)
    
    # Base URL for Apple emojis
    base_url = "https://emojigraph.org/apple/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    }
    
    # Get main page
    print(f"Fetching main page: {base_url}")
    response = requests.get(base_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to access main page: {response.status_code}")
        return
    
    # Parse main page
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find all emoji links
    emoji_links = []
    for link in soup.find_all("a", class_="pim"):
        emoji_name = link.get("href").strip("/").split("/")[-1]
        if "skin-tone" not in emoji_name:
            emoji_links.append({
                "url": "https://emojigraph.org" + link.get("href"),
                "name": emoji_name,
                "processed": emoji_name.replace("-", " ") + " emoji"
            })
    
    total = len(emoji_links)
    print(f"Found {total} emoji links")
    
    # Optional: Choose to download all or limit the number
    # emoji_links = emoji_links[:100]  # Uncomment to limit
    
    # Process emojis
    successful = 0
    failed = 0
    
    # Option 1: Sequential processing (slower but more reliable for websites with anti-scraping)
    # for index, emoji in enumerate(emoji_links):
    #     # Random delay between requests
    #     time.sleep(random.uniform(0.5, 1.5))
        
    #     if download_emoji(emoji, index, total):
    #         successful += 1
    #     else:
    #         failed += 1
    
    # Option 2: Parallel processing (faster but may trigger rate limiting)
    # Uncomment this section and comment out the sequential processing above if you want to try parallel
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_emoji = {executor.submit(download_emoji, emoji, index, total): (emoji, index) 
                          for index, emoji in enumerate(emoji_links)}
        
        for future in concurrent.futures.as_completed(future_to_emoji):
            emoji, index = future_to_emoji[future]
            try:
                if future.result():
                    successful += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Error with {emoji['name']}: {str(e)}")
                failed += 1
    
    
    print(f"\n✅ Download complete!")
    print(f"✅ Successfully downloaded: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Success rate: {successful/total*100:.1f}%")

if __name__ == "__main__":
    main()
