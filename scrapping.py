import requests
import json
import time


COOKIES = {
    "_t":""
}

BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"

HEADERS = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}


session = requests.Session()
session.headers.update(HEADERS)
session.cookies.update(COOKIES)

thread_ids = [168825 , 168943 , 168901 , 168987 , 168537 , 169045 , 168449 , 99838 , 169247 , 166576 , 169352 , 
              169456 , 169393 , 168506 , 168832 , 169369 , 169807 , 170131 , 170147 , 170309 , 170413 , 171054 , 
              171428 , 171473 , 171422 , 171515 ,166647 , 166738 , 166593 , 167072 , 166891 , 164214 , 167172 , 
              166866 , 167699 , 167410 , 167471 , 167415 , 167471 , 167415 , 167344 , 167679 , 166816 , 167679 , 
              166816 , 167878 , 168017 , 168057 , 168143 , 165959 , 168142 , 168303 , 168310 , 168011 , 168482 , 
              168458 , 168384 , 168567 , 168515 , 166651 , 168476 , 141413 , 161214 , 163144 , 161072 , 163147 , 163224 , 
              163241 , 163381 , 164089 , 164205 , 163765 , 164147 , 164291 , 164460 , 164462 , 164737 , 164869 , 165142 , 
              163158 , 165593 , 165746 ,165830 , 165922,165396,166100,165687,166349,166357,166303,161120,165433,165416,166498,166634 ,162425]


for tid in thread_ids:
    api_url = f"{BASE_URL}/t/{tid}.json"
    response = session.get(api_url)

    if response.status_code == 200:
        data = response.json()
        
        # Extract slug from the response
        slug = data.get("slug", "unknown-slug")
        
        # Construct actual browser URL
        actual_url = f"{BASE_URL}/t/{slug}/{tid}"
        
        # Add both URLs to the data
        data["_api_url"] = api_url
        data["_actual_url"] = actual_url

        # Save to file
        with open(f"thread_{tid}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Saved thread {tid} -> {actual_url}")
    else:
        print(f"Failed to fetch thread {tid}: {response.status_code}")

    time.sleep(1)  # Be polite
