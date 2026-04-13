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
        pack_and_act = (packet, action)
        self.connections.add(pack_and_act)
        pass
