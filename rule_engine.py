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

        for i in range(4):
            if rule_dict[i] != "ANY" and rule_dict[i] != packet[pkt_keys[i]]:
                return False
        return True



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
        matched = False
        for rule in self.rules:
            matched = rule.matches(packet)
            if matched:
                return rule.action
        return "DROP"

