#pip install cloudflare
# 1. Initialize the client
# It will automatically look for CLOUDFLARE_API_TOKEN in your env variables
#https://developers.cloudflare.com/api/python/resources/radar/subresources/bgp/subresources/routes/methods/pfx2as/
import os
from cloudflare import Cloudflare

client = Cloudflare(
    api_token=os.environ.get("CLOUDFLARE_API_TOKEN"),  # This is the default and can be omitted
)
response = client.radar.bgp.routes.pfx2as()
print(response.meta)


'''


# 1. Initialize the client
# It will automatically look for CLOUDFLARE_API_TOKEN in your env variables
client = Cloudflare(
    api_token=os.environ.get("CLOUDFLARE_API_TOKEN")
)

def get_asn_for_prefix(prefix):
    try:
        # 2. Query the Radar BGP Route API (Prefix to AS mapping)
        response = client.radar.bgp.routes.pfx2as(prefix=prefix)
        
        # 3. Parse the results
        for entry in response.prefix_to_asn:
            print(f"Prefix: {entry.prefix}")
            print(f"Origin ASN: AS{entry.asn}")
            print(f"Name: {entry.name}")
            print(f"RPKI Status: {entry.rpki_validation_state}")
            print("-" * 20)
            
    except Exception as e:
        print(f"Error: {e}")

# Example usage: Look up Google's public DNS prefix
get_asn_for_prefix("8.8.8.0/24")
'''