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
        return False

    def update(self, packet, action):
        # TODO: implement TCP state tracking
        pass
