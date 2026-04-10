class Rule:
    def __init__(self, action, protocol, src, dst, dport):
        self.action = action
        self.protocol = protocol
        self.src = src
        self.dst = dst
        self.dport = dport

    def matches(self, packet):
        """
        Evaluates whether packet contains matching src_ip, dst_ip, dst_port, and protcol
        Args:
            packet: dictionary containing keys "src_ip", "dst_ip","src_port","dst_port", "protocol","flags"

        Returns:
            boolean: returns whether or not the packet matches a certain rule
        """
        rule_dict = [self.src, self.dst, self.dport, self.protocol]
        pkt_keys = ["src_ip","dst_ip","dst_port","protocol"]

        matches = False

        for i in range(4):
            if rule_dict[i] == "ANY":
                matches = True
            elif rule_dict[i] == packet[pkt_keys[i]]:
                matches = True
            else:
                return False
        return matches



class RuleEngine:
    def __init__(self, rules):
        self.rules = rules

    def match(self, packet):
        """
        Evaluates whether a packet contains matches a rule in self.rules
        Args:
            packet: dictionary containing keys "src_ip", "dst_ip","src_port","dst_port", "protocol","flags"

        Returns:
            boolean: returns rule.action for first rule that matches the packet
                     returns "DROP" if there is no matching rule
        """   
        match = False
        for rule in self.rules:
            print("match check ", rule)
            match = rule.matches(packet)
            if match:
                print("matched! ", rule.action)
                return rule.action
        print("no matching packets")
        return "DROP"


"""
def test():
    pkt = {
        "src_ip": "10.0.0.1",
        "dst_ip": "1.1.1.1",
        "src_port": 1234,
        "dst_port": 80,
        "protocol": "TCP",
        "flags": []
    }
    
   

    rules = RuleEngine([Rule("ALLOW", "TCP", "ANY", "ANY", 80),Rule("DROP", "TCP", "ANY", "ANY", 80)])
    result = rules.match(pkt)
    
    print(result)


if __name__ == "__main__":
    test()
"""