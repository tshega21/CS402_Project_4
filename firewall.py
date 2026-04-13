from rule_engine import RuleEngine
from state_table import StateTable
import logging

class Firewall:
    def __init__(self, rules):
        #Firewall class contains RuleEngine object and StateTable object
        #rule_engine object is passed in
        self.rule_engine = rules
        self.state_table = StateTable()
        self.logger = logging.basicConfig(filename = 'packet_log.txt', level = logging.INFO, format = "%(asctime)s - %(message)s")

    def process_packet(self, packet):
        if self.state_table.is_established(packet):
            #print("is established ",self.state_table.is_established(packet), " ", self.state_table)
            return "ALLOW"

        action = self.rule_engine.match(packet)

        if packet["protocol"] == "TCP":
            self.state_table.update(packet, action)
            #print("updated "  ,self.state_table)

        if action == "DROP" or action == "LOG":
            logging.info(
                f"action: {action}, "
                f"src_ip: {packet['src_ip']}, "
                f"dst_ip: {packet['dst_ip']}, "
                f"src_port: {packet['src_port']}, "
                f"dst_port: {packet['dst_port']}, "
                f"protocol: {packet['protocol']}, "
                f"flags: {packet['flags']}"
            )

        return action
