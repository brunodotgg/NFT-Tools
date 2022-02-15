<h1 align="center">Welcome to NFT-Tools 👋</h1>
<p>
</p>

### Scrapers 

Parasid API

```bash
cd scrapers
python3 parasid_api.py {SLUG} {NUMBER} "{NAME}" "{SYMBOL}"
```
The collection will be saved in `collections/paras.id/{SLUG}`

### Processors

Rarity Checker

```bash
cd processors
python3 calculate_rarity.py {SLUG} "{PLATFORM}" 
```
The collection metadata will be updated and can be found in `collections/paras.id/{SLUG}/metadata`