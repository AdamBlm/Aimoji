import os
from PIL import Image

def replace_transparent_with_white():
    emojis_dir = './emojis'
    processed_count = 0
    failed_count = 0
    
    # Ensure the directory exists
    if not os.path.exists(emojis_dir):
        print(f"❌ Error: Directory '{emojis_dir}' does not exist")
        return
    
    # Get all PNG files
    png_files = [f for f in os.listdir(emojis_dir) if f.endswith('.png')]
    total_files = len(png_files)
    
    print(f"🔍 Found {total_files} PNG files to process")
    
    # Process each file
    for index, filename in enumerate(png_files):
        try:
            file_path = os.path.join(emojis_dir, filename)
            print(f"🔄 Processing {index+1}/{total_files}: {filename}")
            
            # Open the image
            img = Image.open(file_path)
            
            # Check if the image has an alpha channel (transparency)
            if img.mode == 'RGBA':
                # Create a new image with white background
                white_bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
                
                # Paste the original image onto the white background
                white_bg.paste(img, (0, 0), img)
                
                # Convert to RGB (removing alpha channel)
                white_bg = white_bg.convert('RGB')
                
                # Save the new image, replacing the original
                white_bg.save(file_path, 'PNG')
                print(f"✅ Replaced transparent background with white: {filename}")
                processed_count += 1
            else:
                print(f"ℹ️ No transparency to replace in: {filename}")
                processed_count += 1
                
        except Exception as e:
            print(f"❌ Error processing {filename}: {str(e)}")
            failed_count += 1
    
    print(f"\n✅ Process complete!")
    print(f"✅ Successfully processed: {processed_count}")
    print(f"❌ Failed: {failed_count}")
    
if __name__ == "__main__":
    replace_transparent_with_white()
