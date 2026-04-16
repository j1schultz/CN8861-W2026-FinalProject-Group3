import pybgpstream
import os
import time
import csv
from datetime import datetime, timedelta
import pandas as pd

#merge Cho et al. datasets 
#reading in each dataset as a pandas dataframe
cho_data = 'cho_datasets/results_news_updated_2.csv'
cho_new_data = 'cho_datasets/news_updated.csv'
cho_df = pd.read_csv(cho_data)
cho_updated = pd.read_csv(cho_new_data)

#adjusting column names to match
cho_df["new_title"] = cho_df["title"].str.split('.').str[0]
prepend_row = {"title":"prepend_135700", "start_time":"2018-04-28T12:55:48","prefix":"131.108.159.0/24"}
cho_new_df = pd.concat([cho_updated, pd.DataFrame([prepend_row])], ignore_index=True)
cho_new_df["new_title"] = cho_new_df["title"]
cho_new_df["vt_pfx"] = cho_new_df["prefix"]

#merging the 2 files based on the title and prefix
merged_cho = pd.merge(cho_df, cho_new_df, on=['new_title', 'vt_pfx'])

#converting time to an acceptable format for BGPStream
merged_cho['converted_start_time'] = pd.to_datetime(merged_cho['start_time'])
merged_cho['converted_end_time'] = merged_cho['converted_start_time'] + pd.Timedelta(hours=24)
merged_cho['formatted_start_time'] = merged_cho['converted_start_time'].dt.tz_localize('UTC').dt.strftime('%Y-%m-%d %H:%M:%S %Z')
merged_cho['formatted_end_time'] = merged_cho['converted_end_time'].dt.tz_localize('UTC').dt.strftime('%Y-%m-%d %H:%M:%S %Z')

#input: element from bgpstream
#output: all element fields
def check_stream(element):
    required_fields = ["prefix", "next-hop", "communities", "as-path"]
    fields_dict = {}
    #if the field doesn't exist make the value None
    for k in required_fields:
        if k not in element.fields:
            fields_dict[k] = "None"
        else:
            fields_dict[k] = element.fields[k]
    return fields_dict

#input: start time, end time, prefix, event name
#output: creates a csv file with BGPStream data
def pull_bgp_data(start, end, prefix, event):

    #setting filters for BGPStream
    stream = pybgpstream.BGPStream(
        from_time=start, until_time=end,
        collectors=["route-views.sg", "route-views.eqix"],
        filter= f"prefix more {prefix}"
    )
    stream.set_data_interface_option("broker", "cache-dir", "./cache_folder_1")

    bgp_event_data = []
    for elem in stream:
        fields_values = check_stream(elem)
        clean_elem = {
            "record_type": elem.record.type,
            "time": elem.time,
            "type": elem.type,
            "peer_address": elem.peer_address
        }

        full_dict = clean_elem | fields_values
        bgp_event_data.append(full_dict)

    #create a file for given time frame of the current event
    if len(bgp_event_data) != 0:        
        keys = bgp_event_data[0].keys()
        with open(f'./bgpdata_collection/{event}_{start}_{end}.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(bgp_event_data)
    else:
        #if no data was retrieved for the given time make a note in "no_data.csv"
        with open('no_data.csv', 'a') as file:
            writer = csv.writer(file)
            writer.writerow([f"no events during: {event}{start}-{end} \n"])


#input: start time, end time, prefix, event name
#output: calls functions to create bgp event .csv files
def retrieve_event(start_str, end_str, prefix, event_name):
    #format Start Time and End Time to be put int BGPStream data collection
    fmt = "%Y-%m-%d %H:%M:%S %Z"
    current_timeframe = datetime.strptime(start_str, fmt)
    end_timeframe = datetime.strptime(end_str, fmt)

    #loop through the entire start time to end time
    while current_timeframe <= end_timeframe:
        start_time = time.perf_counter()
        temp_end = current_timeframe + timedelta(hours=1)
        #collect BGPStream data in 1 hour increments
        pull_bgp_data(str(current_timeframe),str(temp_end), prefix, event_name)
        current_timeframe += timedelta(hours=1)

        end_time = time.perf_counter()
        print(f"Elapsed time: {end_time - start_time:0.4f} seconds")


#use Cho et al. dataset to gather BGPStream data
for i in merged_cho.to_dict('records'):
    #if prefix was missing skip and move to the next record
    if type(i['prefix']) == float:
        continue
    else:
        retrieve_event(i["formatted_start_time"], i["formatted_end_time"], i["vt_pfx"], i["new_title"])

#saved cho data for later use
merged_cho.to_csv('cho_datasets/all_cho_data.csv', index=False)
