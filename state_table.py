class StateTable:
    def __init__(self):
        self.connections = set()

    def _key(self, packet):
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
