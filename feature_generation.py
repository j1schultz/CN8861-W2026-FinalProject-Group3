import pandas as pd
import Levenshtein

import glob
import os


#--------------------editing-distance--------------------
#trying to guess if we think someone made a typo
#or if someone purposely changed the AS number
cho_new_data = 'cho_datasets/all_cho_data.csv'
cho_df = pd.read_csv(cho_new_data)

cho_sorted = cho_df.sort_values(by='new_title')
'''
#cleaing the hijack AS column so formatting matches victim AS column
def get_hijack_as(hijack_num):
    hijack = str(hijack_num)
    if hijack == None:
        return "None"
    elif "," in hijack:
        return hijack.split(",")
    else:
        return hijack

def levenshtein_distance(victim_as, hijack_as):
    as_1 = victim_as.strip()
    as_2 = hijack_as.strip()
    distance = Levenshtein.distance(as_1,as_2)
    return distance

cho_sorted['levenshtein_distance'] = None
for i, r in cho_sorted.iterrows():
    h_as = get_hijack_as(r["hj_as"])
    v_as = str(r["vt_as"])

    levenshtein_dist = []
    #some events had multiple hijacked ASes
    if type(h_as) != str:
        n = 0
        while n < len(h_as):
            levenshtein_dist.append(levenshtein_distance(v_as, h_as[n]))
            n+=1
    else:
        levenshtein_dist.append(levenshtein_distance(v_as, h_as))
    cho_sorted.at[i, 'levenshtein_distance'] = levenshtein_dist
'''

#--------------------prepending-mistakes--------------------

def match_title(title_list, filename_to_check):
    match_key = ""  # Set a default value first
    for title in title_list:
        if title in filename_to_check:
            match_key = title
            return title

path = 'bgpdata_collection/*.csv'
all_raw_files = glob.glob(path)

#get list of title names
titles_to_group = cho_sorted["new_title"].dropna().astype(str).tolist()

grouped_bgp_data = {}
for file in all_raw_files:
    temp_df = pd.read_csv(file)
    
    filename = os.path.basename(file) 
    temp_df['filename'] = filename 
    
    checked_titled = match_title(titles_to_group, filename)
    temp_df['title'] = checked_titled

    if checked_titled not in grouped_bgp_data:
        # If this is the first file for this title, just save the df
        grouped_bgp_data[checked_titled] = temp_df
    else:
        # If we already have files for this title, concatenate them together
        grouped_bgp_data[checked_titled] = pd.concat([grouped_bgp_data[checked_titled], temp_df], ignore_index=True)



group_df = grouped_bgp_data["backconnect_2"]
unique_as_paths = group_df['as-path'].dropna().unique().tolist()
print(unique_as_paths)