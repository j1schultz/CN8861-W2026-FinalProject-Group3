import pybgpstream
import os


stream = pybgpstream.BGPStream(
    from_time="2018-04-24 11:00:00 UTC", until_time="2018-04-24 11:15:00 UTC",
    collectors=["route-views.sg", "route-views.eqix"],
    record_type="updates",
    filter="prefix more 205.251.192.0/23"
)
stream.set_data_interface_option("broker", "cache-dir", "./cache_folder_1")

def check_stream(element):
    required_fields = ["prefix", "next-hop", "communities", "as-path"]
    fields_dict = {}
    for k in required_fields:
        if k not in elem.fields:
            fields_dict[k] = "None"
        else:
            fields_dict[k] = elem.fields[k]
    return fields_dict

for elem in stream:
    fields_values = check_stream(elem)
    
    #if hijacker_number in as_path:
    clean_elem = {
        "time": elem.time,
        "type": elem.type,
        "peer_address": elem.peer_address
    }

    full_dict = clean_elem | fields_values
    print(full_dict)
    

