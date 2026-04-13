class StateTable:
    def __init__(self):
        # unordered, unique values
        # no indexing, use in keyword, like dict but no value
        self.connections = set()

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
        
        return (forward_keys in set() or backward_keys in set())

    def update(self, packet, action):
        # TODO: implement TCP state tracking
        if packet["protocol"] != "TCP":
            return
        
        #STILL NEED TO FIX
        keys = self._key(packet)

        # think we need to change is_established to track the action as 
        # well and return he action if established instead of auto allow

        # then track keys, action, and state (syn, syn-ack, or ack)
        # if syn, create new entry, if syn-ack and is established with state = syn, 
        # update state to syn-ack, if ack, check if established and state = syn-ack, 
        # update to ack, otherwise for all, drop (add to table but change action to drop)
        flags = packet.get("flags", []) 
        if "SYN" in flags:
            if "ACK" not in flags:
                state = (keys, "SYN")
                self.connections.add(state)
        pass
