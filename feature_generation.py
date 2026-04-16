import pandas as pd
import Levenshtein
import glob
import os
import re

#path to Cho et al. data
cho_new_data = 'cho_datasets/all_cho_data.csv'
cho_df = pd.read_csv(cho_new_data)
cho_sorted_df = cho_df.sort_values(by='new_title')

#path to raw bgp data
full_path_toBGP = 'bgpdata_collection/*.csv'
path_to_merged = "bgpdata_collection/bgpdata_merged/"

#--------------------merging bgp data by event--------------------
#input: list of all event names, current event name
#output: retrieve current event name
def match_title(title_list, filename_to_check):
    match_key = "" 
    for title in title_list:
        if title in filename_to_check:
            match_key = title
            return title


#input: Cho et al. data, path to raw BGP data
#output: .csv for each event
def merge_bgp_data(all_cho, path):
    all_raw_files = glob.glob(path)

    #get list of title names
    titles_to_group = all_cho["new_title"].dropna().astype(str).tolist()

    #for each event merge individual csv files into 1 file
    grouped_bgp_data = {}
    for file in all_raw_files:
        temp_df = pd.read_csv(file)
        filename = os.path.basename(file) 
        temp_df['filename'] = filename 
        
        checked_titled = match_title(titles_to_group, filename)
        temp_df['title'] = checked_titled

        output_file = os.path.join(f"{path_to_merged}", f"ALL-{checked_titled}.csv")
        file_exists = os.path.isfile(output_file)
        temp_df.to_csv(output_file, mode='a', index=False, header=not file_exists)
    
    return f"Files saved {filename}"

#--------------------editing-distance--------------------
#input: hijacked AS number
#output: cleaned hijacked AS number
def get_hijack_as(hijack_num):
    hijack = str(hijack_num)
    if hijack == None:
        return "None"
    elif "," in hijack:
        return hijack.split(",")
    else:
        return hijack

#input: victim AS number, hijacked AS number
#output: Levenshtein distance number
def levenshtein_distance(victim_as, hijack_as):
    as_1 = victim_as.strip()
    as_2 = hijack_as.strip()
    distance = Levenshtein.distance(as_1,as_2)
    return distance

#input: Cho et al. data
#ouptput: Cho et al. data with Levenshtein distance number
def deterimine_levenshtein_distance(cho_sorted):  
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
    return cho_sorted

#--------------------prepending-mistakes--------------------
#input: Cho et al. data
#output: list of prepend AS numbers
def get_prepend(cho_data):
    cho_prepend_only = cho_data[cho_data['category_x'] == 'prepend']
    cho_prepend_hj = cho_prepend_only["hj_as"].tolist()

    cho_hj = []
    for hj in cho_prepend_hj:
        hj_list = re.split(r"[,']", hj)
        for asn in hj_list:
            try:
                num = float(asn)
                cho_hj.append(asn)
            except (ValueError, TypeError):
                continue

    return cho_hj

#input: Cho et al. AS numbers, BGP Raw AS numbers
#output: True, if Cho etal. AS numbers in BGP Raw AS numbers
def check_rawdata_prepend(prepend_cho, prepend_raw):
    for i in prepend_cho:
        if i in prepend_raw:
            return True
        else:
            return False

#input: Cho et al dataset, Path to BGP raw data
#output: Result if category was prepend or not 
def deterimine_prepending(cho_sorted, path_toBGP):
    prepend_data = get_prepend(cho_sorted)
    all_raw_files = glob.glob(f"{path_toBGP}*.csv")

    for i in all_raw_files:
        merged_data = pd.read_csv(i)

        if 'as-path' not in merged_data.columns:
            print(f"Skipping {i}: 'as-path' column not found.")
            continue
        else:
            unique_as_paths = merged_data['as-path'].dropna().unique().tolist()
            prepend_result = check_rawdata_prepend(prepend_data, unique_as_paths)
            print(f"prepend_result: {prepend_result}")

#--------------------MOAS--------------------
#input: BGPStream data
#output: dictionary of what prefixes MOAS was found or not
def check_MOAS(bgp_data_files):
    all_raw_files = glob.glob(f"{bgp_data_files}*.csv")

    MOAS_check_list = {}
    for i in all_raw_files:
        all_data = pd.read_csv(i)
        
        if 'as-path' not in all_data.columns:
            print(f"Skipping {i}: 'as-path' column not found.")
            continue
        else:
            all_data['origin_as'] = all_data['as-path'].str.split().str[-1]
            origin_counts = all_data.groupby('prefix')['origin_as'].nunique()
            moas_prefixes = origin_counts[origin_counts > 1]
            MOAS_check_list[i] = moas_prefixes
    return MOAS_check_list


#--------------calling functions--------------
#calling each function to process BGP raw data and generate features
deterimine_levenshtein_distance(cho_sorted_df)
merged_data = merge_bgp_data(cho_sorted_df, full_path_toBGP)
deterimine_prepending(cho_sorted_df, path_to_merged)

checkedMOAS = check_MOAS(path_to_merged) 
#in each event checking of MOAS was flagged or not
for k,v in checkedMOAS.items():
    name = k.split("/")[-1]
    if len(v) > 0:
        print(f"{name}: {v}")
    else:
        print(f"{name}: MOAS not found")


