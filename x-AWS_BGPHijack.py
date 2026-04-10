import pybgpstream

# Initialize the BGPStream object
stream = pybgpstream.BGPStream(
    data_interface="broker",
)

# Time interval for the attack: April 24, 2018 (approx 11:00 to 13:00 UTC)
# Format: start_time, end_time (Unix timestamps)
stream.add_interval_filter(1524567600, 1524574800)

# Filter for the target Amazon Route 53 prefix
# The hijack involved more-specific /24s within this /23 range
#stream.add_filter("prefix", "205.251.192.0/23")
stream.add_filter("collector", "rrc00") 
print("Scanning for BGP records involving the 2018 Amazon hijack...")
'''

for rec in stream.records():
    print(f"------------Record------------")
    print(f"Collector: {rec.collector} | Router: {rec.router} | ")
    for elem in rec:
        print("element details")
        for key, value in elem.fields.items():
                print(f"{key}: {value}")

'''
for rec in stream.records():
    for elem in rec:
        # Check if the Attacker ASN (AS10297) is in the AS Path
        as_path = elem.fields.get("as-path", "")
        if "10297" in as_path:
            print(f"Time: {elem.time} | Type: {elem.type} | Prefix: {elem.fields['prefix']} | Path: {as_path}")


import ipaddress

amazon_range = ipaddress.ip_network("205.251.192.0/23")
observed_prefix = ipaddress.ip_network(elem.fields['prefix'])

if observed_prefix.subnet_of(amazon_range) and origin_as != "16509":
    print(f"ALERT: {origin_as} is hijacking Amazon's space!")
