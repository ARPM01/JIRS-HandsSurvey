from serpapi import GoogleSearch
import json


for pages in range (0,50):
    start = pages * 20
    # load the API key from the file
    with open('key.txt') as f:
        api_key = f.readline().strip()
    params = {
    "engine": "google_scholar",
    "q": '("hand" OR "gripper") AND ("manipulation" OR "grasping" OR "grip" OR "skill")',
    "hl": "en",
    "as_ylo": "2019",
    "start": start,
    "num": "20",
    "api_key":  api_key,
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    # save the dictionary to a json file
    with open('data_test/data_'+str(pages)+'.json', 'w') as f:
        f.write(json.dumps(results))
    print("Page: ", pages)
