class StateTable:
    def __init__(self):
        # unordered, unique values
        # no indexing, use in keyword, like dict but no value
        self.connections = set()
    def __str__(self):
        return f"StateTable(connections={self.connections})"

    def _key(self, packet):
        #returns tuple of keys 
        return (
            packet["src_ip"],
            packet["src_port"],
            packet["dst_ip"],
            packet["dst_port"],
        )

    def is_established(self, packet):
        # TODO: check forward/reverse flow
        forward_keys = self._key(packet)
        backward_keys = (forward_keys[2],forward_keys[3],forward_keys[0],forward_keys[1])
        return (forward_keys in self.connections or backward_keys in self.connections)

    def update(self, packet, action):
        """
        - Action is based on rule_engine from firewall
        
        """

        # if packet is UDP etc, do not do TCP state tracking
        if packet["protocol"] != "TCP":
            return
        
        # implement TCP state tracking
        forward_keys = self._key(packet)
        backward_keys = (forward_keys[2],forward_keys[3],forward_keys[0],forward_keys[1])


        flags = packet.get("flags", []) 
        if not flags:
            return action
        if "SYN" in flags and "ACK" not in flags:
                state = (forward_keys)
                self.connections.add(state)



        # think we need to change is_established to track the action as 
        # well and return he action if established instead of auto allow

        # then track keys, action, and state (syn, syn-ack, or ack)
        # if syn, create new entry, if syn-ack and is established with state = syn, 
        # update state to syn-ack, if ack, check if established and state = syn-ack, 
        # update to ack, otherwise for all, drop (add to table but change action to drop)


        #elif "ACK" in flags:
        #      if self.is_established(packet):
                  
             #self.connections.remove(state)
             #state = (forward_keys, "SYN ACK")
             #state.connections.add(state)
        pass
