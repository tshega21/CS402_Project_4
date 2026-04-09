class Rule:
    def __init__(self, action, protocol, src, dst, dport):
        self.action = action
        self.protocol = protocol
        self.src = src
        self.dst = dst
        self.dport = dport

    def matches(self, packet):
        rule_dict = [self.src, self.dst, self.dport, self.protocol]
        pkt_keys = ["src_ip","dst_ip","dst_port","protocol"]

        matches = False

        for i in range(4):
            if rule_dict[i] == "ANY":
                matches = True
            elif rule_dict[i] == packet[pkt_keys[i]]:
                matches = True
            else:
                matches = False

        return matches
        #if match == True:
        #    return self.action
       # else:
        #    return False
            
        # TODO: implement matching logic
        #ret
        return False


class RuleEngine:
    def __init__(self, rules):
        self.rules = rules

    def match(self, packet):
        match = False
        for rule in self.rules:
             match = rule.matches(packet)
             if match:
                return rule.action
        return "DENY"


def test():
    pkt = {
        "src_ip": "10.0.0.1",
        "dst_ip": "1.1.1.1",
        "src_port": 1234,
        "dst_port": 80,
        "protocol": "TCP",
        "flags": []
    }
    

    rules = RuleEngine([Rule("ALLOW", "TCP", "ANY", "ANY", 23),Rule("DROP", "TCP", "ANY", "ANY", 80)])
    result = rules.match(pkt)
    
    print(result)


if __name__ == "__main__":
    test()
