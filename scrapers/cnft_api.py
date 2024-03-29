
import copy
from pickletools import optimize
import sys
import requests
import os
import json
import math
import ipfsApi
from PIL import Image, ImageOps, ImageTk

collectionName = sys.argv[1]
number = int(sys.argv[2])
newName = sys.argv[3]
symbol = sys.argv[4]
platform = "cnft.io"

headers = {
    'User-Agent': 'PostmanRuntime/7.29.0',
    'Content-Type': 'application/json'
}

print(f"""
slug: {collectionName}
newName: {newName} [{symbol}]
number: {number}
""")

print(f"There are ?? nfts available, we need {number}.")

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

count = number

# cnft.io has 32 assets per page.
iter = math.ceil(count / 32)
print(f"\nBeginning download of \"{collectionName}\"\n\n")

newID = 1

for i in range(iter):
    url = "https://api.cnft.io/market/listings"
    payload = f"{{\"nsfw\": true,\"page\": {i+1},\"project\": \"{collectionName}\",\"smartContract\": false,\"sold\": false,\"search\": \"\",\"priceMax\": null,\"priceMin\": null,\"sort\": {{\"_id\": -1}},\"types\": [\"listing\",\"auction\",\"offer\",\"bundle\"],\"verified\": true}}"
    request = requests.request("POST", url, headers=headers, data=payload)
    request = json.loads(request.content.decode())
    if "results" in request:
        if len(list(request["results"])) > 0:
            last = list(request["results"])[-1]
            for asset in request["results"]:
                if "asset" not in asset:
                    asset["asset"] = asset["assets"][0]
                if "asset" in asset:
                    if(newID > number):
                        exit()
                    sys.stdout.flush()
                    print(
                        f"[{newID}/{number}] {asset['asset']['metadata']['name']}", end='\r')
                    metadata = {
                        "name": f"{newName} #{newID}",
                        "description": f"{newName} #{newID}",
                        "attributes": []
                    }

                    attributes = copy.deepcopy(asset['asset']["metadata"])

                    if attributes["image"]:
                        del attributes["image"]
                    if attributes["name"]:
                        del attributes["name"]

                    for attribute in attributes:
                        if attribute == 'traits':
                            for trait in attributes[attribute]:
                                metadata["attributes"].append({
                                    "trait_type": trait,
                                    "value": attributes[attribute][trait],
                                })

                    dfile = open(
                        f"../collections/{platform}/{collectionName}/metadata/{newID}.json", "w+")
                    json.dump(metadata, dfile, indent=3)
                    dfile.close()
                    if "image" in asset['asset']['metadata']:
                        api = ipfsApi.Client(host='https://ipfs.infura.io', port=5001)
                        image = requests.get(
                            f"https://media.cnft.io/{asset['asset']['metadata']['image'].replace('ipfs://', '').replace('ipfs/', '')}&350", stream=True)
                        # image = requests.get(
                        #     image.content.decode().replace('"', ''), stream=True)
                        extension = "png"
                        # If the URL returns status code "200 Successful", save the image into the "images" folder.
                        if image.ok:
                            file = open(
                                f"../collections/{platform}/{collectionName}/og-art/{newID}.{extension}", "wb+")
                            for block in image.iter_content(1024):
                                if not block:
                                    break
                                file.write(block)
                            newID += 1
print("\nFinished.\n")
