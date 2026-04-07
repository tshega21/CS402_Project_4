import json
from firewall import Firewall
from rule_engine import Rule

rules = [
]

fw = Firewall(rules)

with open("packets.json") as f:
    packets = json.load(f)

for pkt in packets:
    result = fw.process_packet(pkt)
    print(result)
