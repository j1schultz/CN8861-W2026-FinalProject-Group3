import pybgpstream
import os

import time
import csv

from datetime import datetime, timedelta

event_dict = [
    {
        "event_name": "2018_Amazon_",
        "start_str": "2018-04-24 11:00:00 UTC",
        "end_str": "2018-04-24 12:00:00 UTC",
        "prefix": "prefix more 205.251.192.0/24",
        "event_type": "origin_change"
    },
    {
        "event_name": "2016_backconnect_",
        "start_str": "2016-02-20 08:00:00 UTC",
        "end_str": "2016-02-20 09:00:00 UTC",
        "prefix": "prefix more 72.20.0.0/19",
        "event_type": "forged_as_path"
    },
    {
        "event_name": "2011_facebook_",
        "start_str": "2011-03-22 07:00:00 UTC",
        "end_str": "2011-03-22 16:00:00 UTC",
        "prefix": "prefix more 69.171.255.0/24",
        "event_type": "forged_as_path"
    },
    {
        "event_name": "2018_MEGANET_",
        "start_str": "2018-04-28 12:00:00 UTC",
        "end_str": "2018-04-29 12:00:00 UTC",
        "prefix": "prefix more 131.108.159.0/24",
        "event_type": "prepend"
    },
    {
        "event_name": "2016_TIM_",
        "start_str": "2016-05-20 21:00:00 UTC",
        "end_str": "2016-05-21 21:00:00 UTC",
        "prefix": "prefix more 191.86.128.0/19",
        "event_type": "typo"
    }
]



def check_stream(element):
    required_fields = ["prefix", "next-hop", "communities", "as-path"]
    fields_dict = {}
    for k in required_fields:
        if k not in element.fields:
            fields_dict[k] = "None"
        else:
            fields_dict[k] = element.fields[k]
    return fields_dict


def pull_bgp_data(start, end, prefix, event):
    stream = pybgpstream.BGPStream(
        from_time=start, until_time=end,
        collectors=["route-views.sg", "route-views.eqix"],
        record_type="updates",
        filter=prefix
    )

    stream.set_data_interface_option("broker", "cache-dir", "./cache_folder_1")

    bgp_event_data = []
    for elem in stream:
        fields_values = check_stream(elem)
        
        clean_elem = {
            "time": elem.time,
            "type": elem.type,
            "peer_address": elem.peer_address
        }

        full_dict = clean_elem | fields_values
        bgp_event_data.append(full_dict)

    if len(bgp_event_data) != 0:        
        keys = bgp_event_data[0].keys()
        with open(f'{event}_{start}_{end}.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(bgp_event_data)
    else:
        with open('no_data.csv', 'a') as file:
            writer = csv.writer(file)
            writer.writerow([f"no events during: {event}{start}-{end} \n"])


def retrieve_event(start_str, end_str, prefix, event_name):
    fmt = "%Y-%m-%d %H:%M:%S %Z"
    current_timeframe = datetime.strptime(start_str, fmt)
    end_timeframe = datetime.strptime(end_str, fmt)

    while current_timeframe <= end_timeframe:
        start_time = time.perf_counter()
        temp_end = current_timeframe + timedelta(hours=1)
        
        pull_bgp_data(str(current_timeframe),str(temp_end), prefix, event_name)
        current_timeframe += timedelta(hours=1)

        end_time = time.perf_counter()
        print(f"Elapsed time: {end_time - start_time:0.4f} seconds")


for i in event_dict:
    retrieve_event(i["start_str"], i["end_str"], i["prefix"], i["event_name"])