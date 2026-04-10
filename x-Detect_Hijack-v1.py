from pybgpstream import BGPStream

# 1. Define your target and authorized AS
TARGET_PREFIX = "2001:db8::/32"  # Replace with your prefix
AUTHORIZED_AS = "64496"           # Replace with your actual ASN

# 2. Initialize the stream (Real-time or Historical)
stream = BGPStream(
    from_time="2026-03-20 00:00:00", 
    until_time="2026-03-20 01:00:00",
    collectors=["rrc00", "route-views2"],
    record_type="updates"
)

# 3. Add a filter for the specific prefix you want to watch
stream.add_filter("prefix", TARGET_PREFIX)

print(f"Monitoring {TARGET_PREFIX} for hijacks...")

# 4. Iterate through records and elements
for rec in stream.records():
    for elem in rec:
        # We only care about Announcements ("A")
        if elem.type == "A":
            as_path = elem.fields.get("as-path", "")
            if as_path:
                # The Origin AS is the last item in the path
                origin_asn = as_path.split()[-1]
                
                # Check for mismatch
                if origin_asn != AUTHORIZED_AS:
                    print(f"⚠️ SUSPICIOUS HIJACK DETECTED!")
                    print(f"Prefix: {elem.fields['prefix']}")
                    print(f"Detected Origin: AS{origin_asn} (Unauthorized)")
                    print(f"Full Path: {as_path}")
                    print(f"Collector: {rec.collector}")
