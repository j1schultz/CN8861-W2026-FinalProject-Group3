import pybgpstream
import pickle
import os
#pip install tqdm
from tqdm import tqdm


cache_path = "./cache_folder_1"
if not os.path.exists(cache_path):
    os.makedirs(cache_path)
    print(f"Created cache directory at {cache_path}")


# Initialize the BGPStream object
stream = pybgpstream.BGPStream(data_interface="broker")

# YouTube Hijack: Feb 24, 2008 (approx 18:47 to 21:00 UTC)
# 1203878820 = Feb 24 2008 18:47:00 UTC
# 1203886800 = Feb 24 2008 21:00:00 UTC
# Filter for the specific hijacked prefix
#stream.add_filter("prefix", "208.65.153.0/24")
#print("Scanning for BGP records involving the 2008 YouTube hijack...")
#hijacker_number = "17557"


start_ts = 1524567600  # 11:00
end_ts = 1524576600    # 13:30
interval = 15 * 60     # 15 minutes in seconds


# April 24, 2018 Time Window (Approx 11:00 to 13:30 UTC)
# 1524567600 = Apr 24 2018 11:00:00 UTC
# 1524576600 = Apr 24 2018 13:30:00 UTC
#stream.add_interval_filter(1524567600, 1524576600)
# Filter for the target Amazon Route 53 prefixes (205.251.192.0/23 ranges)
# The hijackers announced /24s within these blocks
stream.add_filter("prefix", "205.251.192.0/23")
stream.set_data_interface_option("broker", "cache-dir", cache_path)
hijacker_number = "10297"

# Using a reliable collector for 2008 data (rrc00 or route-views2)
stream.add_filter("collector", "rrc00") 

print("Scanning for BGP records involving the 2018 Amazon hijack...")

def get_elements(records):
    bgp_event_list = []
    #for rec in stream.records():
    #for rec in tqdm(stream.records(), desc="Processing BGP Records"):
    for rec in tqdm(records, desc="Processing BGP Records"):
        for elem in rec:
            # Filter for the malicious AS (Pakistan Telecom AS17557) in the path
            as_path = elem.fields.get("as-path", "")
            prefix = elem.fields.get("prefix", "")
            if hijacker_number in as_path:
                clean_elem = {
                            "time": elem.time,
                            "type": elem.type,
                            "prefix": prefix,
                            "peer_address": elem.peer_address,
                            "next-hop": elem.fields["next-hop"],
                            "communities": elem.fields["communities"],
                            "peer_asn": as_path
                        }
                bgp_event_list.append(clean_elem)
    return bgp_event_list

def create_file(bgp_events, interval, event_name):
    # Save to a file
    with open(f"{event_name}{interval}.pkl", "wb") as f:
        pickle.dump(bgp_events, f)
    print(f"Success! Saved {len(bgp_event_list)} records to youtube_hijack_data.pkl")


current = start_ts
while current < end_ts:
    next_ts = current + interval
    stream.add_interval_filter(current, next_ts)

    stream.add_filter("prefix", "205.251.192.0/23")
    stream.set_data_interface_option("broker", "cache-dir", cache_path)
    hijacker_number = "10297"
    stream.add_filter("collector", "rrc00") 

    events = get_elements(stream.records())

    name = "Amazon_2018_"
    time_range = (f"{current}-{next_ts}")
    create_file(events, time_range, name)

    current = next_ts