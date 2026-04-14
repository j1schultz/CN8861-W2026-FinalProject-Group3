import glob
import pandas as pd

# 1. Define the path and find all .csv files
path = 'bgpdata_collection/*.csv'
all_files = glob.glob(path)

# 2. Read all files into a list of DataFrames
df_list = [pd.read_csv(f) for f in all_files]

#print(df_list[0])
# 3. (Optional) Combine them into one large DataFrame
#combined_df = pd.concat(df_list, ignore_index=True)


#pip install python-Levenshtein
#--------------------editing-distnce--------------------
#trying to guess if we think someone made a typo
#or if someone purposely changed the AS number
#using the previous work of cho to map the hijacked AS and victim AS

#TO-DO: Calculate the distribution of distance - average, mean, mode, median

import Levenshtein
cho_new_data = 'cho_datasets/news_updated.csv'
cho_df = pd.read_csv(cho_new_data)
#coming in as a float
#print(cho_df["victim_as"])

#print(cho_df["hijack_as"])

def get_hijack_as(hijack_num):
    hijack = str(hijack_num)
    if hijack == None:
        return "None"
        #print("none")
    elif "," in hijack:
        return hijack.split(",")
    else:
        return hijack

def get_victim_as(victim_num, title):
    victim = str(victim_num)
    return victim


def levenshtein_distance(victim_as, hijack_as):
    #print(f"victim_as: {victim_as}, hijack_as: {hijack_as}")
    as_1 = victim_as.strip()
    as_2 = hijack_as.strip()

    # Calculate the absolute edit distance
    distance = Levenshtein.distance(as_1, as_2)

    print(f"The Levenshtein distance is: {distance}") 
    # Output: 3 (k->s, e->i, add 'g')

for i, r in cho_df.iterrows():
    h_as = get_hijack_as(r["hijack_as"])
    v_as = str(r["victim_as"])

    #print(i, type(h_as))
    #levenshtein_distance(v_as, h_as)
    
    if type(h_as) != str:
        n = 0
        while n < len(h_as):
            levenshtein_distance(v_as, h_as[n])
            n+=1
    else:
        levenshtein_distance(v_as, h_as)
    #v_as = get_victim_as(r["victim_as"], r["title"])
    #print(f"{i} - h_as: {h_as}")
    #print(f"{i} - v_as: {v_as}")
    
    

