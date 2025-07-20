import json

def find_products(query):
    with open('products.json') as f:
        products = json.load(f)

    query = query.lower()
    results = []

    for p in products:
        if "white" in query and "white" not in p["color"].lower():
            continue
        if "shoes" in query and "shoes" not in p["title"].lower() and "sneakers" not in p["title"].lower():
            continue
        if "under" in query:
            try:
                price_limit = int(query.split("under rs")[1].split()[0])
                if p["price"] > price_limit:
                    continue
            except:
                pass
        results.append(p)

    return results
