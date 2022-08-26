
from pickletools import optimize
import sys
import time
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

throttled = True

while(throttled):
    collection = requests.get(f"https://api.opensea.io/collection/{collectionName}?format=json", headers=headers)

    collection = json.loads(collection.content.decode())
    if('detail' in collection and collection['detail'] == 'Request was throttled.'):
        print(f"\nRequest was throttled. Retrying in 60 seconds\n")
        time.sleep(60)
    else: 
        throttled = False


    

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
per_page = 200

# Parasid limits to 30 assets per API request.
iter = math.ceil(count / per_page)
print(f"\nBeginning download of \"{collectionName}\"\n\n")

newID = 1
for i in range(iter):
    offset = i * per_page
    throttled = True

    while(throttled):
        url = f"https://api.opensea.io/assets?order_direction=desc&offset={offset}&limit={per_page}&collection={collectionName}&format=json"
        request = requests.get(url, headers=headers, timeout=(5, 15))
        request = json.loads(request.content.decode())
        if('detail' in request and request['detail'] == 'Request was throttled.'):
            print(f"\nRequest was throttled. Retrying in 60 seconds\n")
            time.sleep(60)
        else: 
            throttled = False
    
    if "assets" in request and len(request["assets"]) > 0:
        print(f"\n{url}")
        for asset in request["assets"]:
            sys.stdout.write('\033[2K\033[1G')
            print(f"[{newID}/{number}] {asset['name']}", end='\r')
            if(os.path.exists(f"../collections/{platform}/{collectionName}/metadata/{newID}.json")):
                newID += 1
                continue
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
            
            image = requests.get(asset['image_url'], headers=headers, timeout=(5, 15))

            extension = image.headers['content-type'].replace("image/", "")
            # If the URL returns status code "200 Successful", save the image into the "images" folder.
            if not image == {} and image.status_code == 200:
                file = open(f"../collections/{platform}/{collectionName}/og-art/{newID}.{extension}", "wb+")
                file.write(image.content)
                file.close()
                newID += 1
            else:
                print(f"Error downloading image for {asset['name']}")
                os.remove(f"../collections/{platform}/{collectionName}/metadata/{newID}.json")
    else:
        print(f"No assets found for {collectionName} @ {url}")
print("\nFinished.\n")