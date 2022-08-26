
from pickletools import optimize
import sys
import requests
import os
import json
import math
from PIL import Image, ImageOps, ImageTk

collectionName = sys.argv[1].lower()
number = int(sys.argv[2])
newName = sys.argv[3]
symbol = sys.argv[4]
platform = "opensea.io"

headers = {
    'User-Agent': 'PostmanRuntime/7.29.0',
}

print(f"""
slug: {collectionName}
newName: {newName} [{symbol}]
number: {number}
""")

collection = requests.get(f"https://api.opensea.io/collection/{collectionName}?format=json", headers=headers)

collection = json.loads(collection.content.decode())

if not collection["collection"]["name"]:
    print("Error with parsing the collection.")

print(f"There are {collection['collection']['stats']['total_supply']} nfts available, we need {number}.")

# Create image folder if it doesn't exist.
if not os.path.exists('../collections/'):
    os.mkdir('../collections/')

if not os.path.exists(f"../collections/{platform}"):
    os.mkdir(f"../collections/{platform}")

if not os.path.exists(f'../collections/{platform}/{collectionName}'):
    os.mkdir(f'../collections/{platform}/{collectionName}')

if not os.path.exists(f'../collections/{platform}/{collectionName}/og-art'):
    os.mkdir(f'../collections/{platform}/{collectionName}/og-art')

if not os.path.exists(f'../collections/{platform}/{collectionName}/metadata'):
    os.mkdir(f'../collections/{platform}/{collectionName}/metadata')

count = collection['collection']['stats']['total_supply']
per_page = 30

# Parasid limits to 30 assets per API request.
iter = math.ceil(count / per_page)
print(f"\nBeginning download of \"{collectionName}\"\n\n")

newID = 1

for i in range(iter):
    offset = i * per_page
    request = requests.get(f"https://api.opensea.io//assets?order_direction=desc&order_by=sale_price&offset={offset}&limit={per_page}&collection={collectionName}&format=json", headers=headers)
    request = json.loads(request.content.decode())
    if "assets" in request:
        for asset in request["assets"]:
            # sys.stdout.flush()
            print(f"[{newID}/{number}] {asset['name']}", end='\r')
            metadata = {
                "name": f"{newName} #{newID}",
                "description": f"{newName} #{newID}",
                "attributes": []
            }

            if "traits" in asset:
                for trait in asset["traits"]:
                    metadata["attributes"].append({
                        "name": trait["trait_type"],
                        "value": trait["value"]
                    })

            dfile = open(f"../collections/{platform}/{collectionName}/metadata/{newID}.json", "w+")
            json.dump(metadata, dfile, indent=3)
            dfile.close()
            
            image = requests.get(asset['image_url'], headers=headers)

            extension = image.headers['content-type'].replace("image/", "")
            # If the URL returns status code "200 Successful", save the image into the "images" folder.
            if not image == {} and image.status_code == 200:
                file = open(f"../collections/{platform}/{collectionName}/og-art/{newID}.{extension}", "wb+")
                file.write(image.content)
                file.close()
                newID += 1
print("\nFinished.\n")