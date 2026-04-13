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
        
        return ((forward_keys,"ESTABLISHED") in self.connections or (backward_keys, "ESTABLISHED") in self.connections)

    def update(self, packet, action):
        """
        - Updates connection state tables and detects SYN, SYN-ACK, and ACK sequence
        - Drops packet if there is not a corresponding entry in connection table
            ex. SYN-ACK but no corresponding SYN in table 
        - Drops packet if there is already entry in connection table
            ex. A SYN packet is sent following a SYN packet from the same source to the same destination
                The second SYN packet is dropped
         Args:
            packet: dictionary containing keys "src_ip", "dst_ip","src_port","dst_port", "protocol","flags"
            action: result from if packet matches any rule in rule_engine 
                - taken into consideration for packets with no existing connection 
        Returns:
            action: returns :ALLOW or DROP based on update taken 

        
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
    
        # Does not allow packets with SYN flag if they do not match the rule engine
        if "SYN" in flags and "ACK" not in flags and action != "DROP":
            state = (forward_keys, "SYN")
            # If same packet with SYN is already in table, do not allow
            if (state in self.connections):
                return "DROP"
            else:
                self.connections.add(state)
                return "ALLOW"

        # Does not test drop as reverse flow might not match rule engine
        elif "SYN" in flags and "ACK" in flags: 
            state = (backward_keys,"SYN")
            # If matching syn, update connection to SYN ACK
            if (state in self.connections):
                self.connections.remove(state)
                state = (forward_keys, "SYN ACK")
                self.connections.add(state)
                return "ALLOW"
            # otherwise, drop packet
            else:
                return "DROP"
            
        elif "SYN" not in flags and "ACK" in flags:
            # if matching syn ack, update connection to established
            state = (backward_keys,"SYN ACK")
            if (state in self.connections):
                self.connections.remove(state)
                state = (forward_keys, "ESTABLISHED")
                self.connections.add(state)
                return "ALLOW"
            # otherwise drop packet
            else:
                return "DROP"
        # if flags do not match TCP handshake flags, drop packet
        else:
            return "DROP"
            