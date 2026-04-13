from rule_engine import RuleEngine
from state_table import StateTable


class Firewall:
    def __init__(self, rules):
        #Firewall class contains RuleEngine object and StateTable object
        #rule_engine object is passed in
        self.rule_engine = rules
        self.state_table = StateTable()

    def process_packet(self, packet):
        if self.state_table.is_established(packet):
            return "ALLOW"
        # think we should change this to the action of the packet

        action = self.rule_engine.match(packet)

        if packet["protocol"] == "TCP":
            self.state_table.update(packet, action)

        return action
