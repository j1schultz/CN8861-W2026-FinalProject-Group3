import pandas as pd

cho_data = 'cho_datasets/results_news_updated_2.csv'
cho_new_data = 'cho_datasets/news_updated.csv'

cho_df = pd.read_csv(cho_data)
cho_new_df = pd.read_csv(cho_new_data)

cho_df["new_title"] = cho_df["title"].str.split('.').str[0]
cho_new_df["new_title"] = cho_new_df["title"]

cho_new_df["vt_pfx"] = cho_new_df["prefix"]

merged_cho = pd.merge(cho_df, cho_new_df, on=['new_title', 'vt_pfx'])
merged_cho['converted_start_time'] = pd.to_datetime(merged_cho['start_time'])
merged_cho['converted_end_time'] = merged_cho['converted_start_time'] + pd.Timedelta(hours=24)

merged_cho['formatted_start_time'] = merged_cho['converted_start_time'].dt.tz_localize('UTC').dt.strftime('%Y-%m-%d %H:%M:%S %Z')
merged_cho['formatted_end_time'] = merged_cho['converted_end_time'].dt.tz_localize('UTC').dt.strftime('%Y-%m-%d %H:%M:%S %Z')


