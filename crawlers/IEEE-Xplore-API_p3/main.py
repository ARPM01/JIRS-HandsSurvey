import xplore
import ast
import pandas as pd
import sys
import time
import json

file_key = open('key.txt')
key = file_key.readline()
file_key.close()


query_parameter="('hand' OR 'gripper') AND ('manipulation' OR 'grasping' OR 'grip' OR 'skill')"  



max_results = 200
query = xplore.XPLORE(key.strip())
query.booleanText(query_parameter)
query.resultsFilter("start_year","2019")
query.maximumResults(max_results)
start_time = time.time()
data = query.callAPI()
resp_time = time.time()
# save the data to a json file
with open('data_'+str(0)+'.json', 'w') as f:
    f.write(data)


def open_json_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

data=open_json_file("data_0.json")


# get the total number of results
data_len = data["total_records"]

print("Total number of results: ", data_len)

for ind in range(1, int(data_len/max_results)+1):
    start_id=max_results * ind
    query = xplore.XPLORE(key.strip())
    query.booleanText(query_parameter)
    query.resultsFilter("start_year","2024")
    #query.resultsFilter("end_year","2019")
    query.startingResult(start_id)
    query.maximumResults(max_results)
    start_time = time.time()
    data = query.callAPI()
    resp_time = time.time()
    # save the data to a json file
    with open('data_'+str(ind)+'.json', 'w') as f:
        f.write(data)

exit()
