
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
platform = "paras.id"

headers = {
    'User-Agent': 'PostmanRuntime/7.29.0',
}

print(f"""
slug: {collectionName}
newName: {newName} [{symbol}]
number: {number}
""")

collection = requests.get(f"https://api-v2-mainnet.paras.id/collection-stats?collection_id={collectionName}", headers=headers)

collection = json.loads(collection.content.decode())

if not collection["status"] == 1:
    print("Error with parsing the collection.")

print(f"There are {collection['data']['results']['total_cards']} nfts available, we need {number}.")

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

count = collection['data']['results']['total_cards']

# Parasid limits to 30 assets per API request.
iter = math.ceil(count / 30)
print(f"\nBeginning download of \"{collectionName}\"\n\n")

newID = 1

nextID = ''
nextUpdated = ''

for i in range(iter):
    if nextID == '' and nextUpdated == '':
        request = requests.get(f"https://api-v2-mainnet.paras.id/token-series?collection_id={collectionName}&exclude_total_burn=true&__limit=30&__sort=updated_at::-1", headers=headers)
    else:
        request = requests.get(f"https://api-v2-mainnet.paras.id/token-series?collection_id={collectionName}&exclude_total_burn=true&__limit=30&__sort=updated_at::-1&_id_next={nextID}&updated_at_next={nextUpdated}", headers=headers)
    request = json.loads(request.content.decode())
    if "data" in request:
        if "results" in request["data"]:
            if len(list(request["data"]["results"])) > 0:
                last = list(request["data"]["results"])[-1]
                nextID = last["_id"]
                nextUpdated = last["updated_at"]
                for asset in request["data"]["results"]:
                    if(newID > number):
                        exit()
                    sys.stdout.flush()
                    print(f"[{newID}/{number}] {asset['metadata']['title']}", end='\r')
                    metadata = {
                        "name": f"{newName} #{newID}",
                        "description": f"{newName} #{newID}",
                    }

                    if "attributes" in asset["metadata"]:
                        metadata["attributes"] = asset["metadata"]["attributes"] 

                    dfile = open(f"../collections/{platform}/{collectionName}/metadata/{newID}.json", "w+")
                    json.dump(metadata, dfile, indent=3)
                    dfile.close()
                    
                    if "http" not in asset['metadata']['media']:
                        image = requests.get(f"https://paras-cdn.imgix.net/{asset['metadata']['media']}?w=600")
                    else:
                        image = requests.get(asset['metadata']['media'])

                    extension = "png"

                    if "mime_type" in asset["metadata"]:
                        if asset["metadata"]["mime_type"] == "image/gif":
                            extension = 'gif'

                    # If the URL returns status code "200 Successful", save the image into the "images" folder.
                    if not image == {} and image.status_code == 200:
                        file = open(f"../collections/{platform}/{collectionName}/og-art/{newID}.{extension}", "wb+")
                        file.write(image.content)
                        file.close()
                        newID += 1
print("\nFinished.\n")