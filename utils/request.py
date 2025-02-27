import requests
from bs4 import BeautifulSoup
import json

# URL of the emoji page
url = "https://emojigraph.org/apple"
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# List to store emoji details
emoji_list = []

divs = soup.find_all("div", class_="row cva")
for div in divs:
    links = div.find_all("a", class_="pim")
    for link in links:
        href = link.get("href")
        img = link.find("img")
        src = img.get("src") if img else ""
        name = href.strip("/").split("/")[-1]
        
        # Skip skin-tone variants
        if "skin-tone" in name:
            continue
        
        # Construct emoji properties
        link_property = "https://emojigraph.com" + src.replace("/144/", "/")
        processed_property = name.replace("-", " ") + " emoji"
        
        # Append data to list
        emoji_list.append({
            "link": link_property,
            "name": name,
            "processed": processed_property
        })

# Save the emoji data to a JSON file
with open("emoji_list.json", "w") as f:
    json.dump(emoji_list, f, indent=4)

print("Emoji data successfully saved to emoji_list.json")
