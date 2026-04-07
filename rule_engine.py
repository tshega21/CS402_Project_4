class Rule:
    def __init__(self, action, protocol, src, dst, dport):
        self.action = action
        self.protocol = protocol
        self.src = src
        self.dst = dst
        self.dport = dport

    def matches(self, packet):
        # TODO: implement matching logic
        return False


class RuleEngine:
    def __init__(self, rules):
        self.rules = rules

    def match(self, packet):
        # TODO: implement matching logic
        return ""
