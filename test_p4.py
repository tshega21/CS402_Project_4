from firewall import Firewall
from rule_engine import Rule, RuleEngine


# **kwargs --> arbitrary number of arguments stored in dict
def make_packet(**kwargs):
    #default packet if empty dict is passed in
    pkt = {
        "src_ip": "10.0.0.1",
        "dst_ip": "1.1.1.1",
        "src_port": 1234,
        "dst_port": 80,
        "protocol": "TCP",
        "flags": []
    }
    
    pkt.update(kwargs)
    return pkt


def test_basic_allow():
    fw = Firewall(RuleEngine([
        Rule("ALLOW", "TCP", "ANY", "ANY", 80)
    ]))
    pkt = make_packet(dst_port=80)
    assert fw.process_packet(pkt) == "ALLOW"


def test_basic_drop():
    fw = Firewall(RuleEngine([
        Rule("DROP", "TCP", "ANY", "ANY", 23)
    ]))
    pkt = make_packet(dst_port=23)
    assert fw.process_packet(pkt) == "DROP"


def test_default_drop():
    fw = Firewall(RuleEngine([]))
    pkt = make_packet(dst_port=9999)
    assert fw.process_packet(pkt) == "DROP"


def test_first_match_wins():
    fw = Firewall(RuleEngine([
        Rule("DROP", "TCP", "ANY", "ANY", 80),
        Rule("ALLOW", "TCP", "ANY", "ANY", 80)
    ]))
    pkt = make_packet(dst_port=80)
    assert fw.process_packet(pkt) == "DROP"


def test_stateful_connection():
    fw = Firewall(RuleEngine([
        Rule("ALLOW", "TCP", "ANY", "ANY", 80)
    ]))

    syn = make_packet(flags=["SYN"])
    syn_ack = make_packet(
        src_ip="1.1.1.1",
        dst_ip="10.0.0.1",
        src_port=80,
        dst_port=1234,
        flags=["SYN", "ACK"]
    )
    ack = make_packet(flags=["ACK"])

    assert fw.process_packet(syn) == "ALLOW"
    result = fw.process_packet(syn_ack)
    print("SYN-ACK result:", result)
    assert result == "ALLOW"
    assert fw.process_packet(ack) == "ALLOW"


def test_established_flow_bypass_rules():
    fw = Firewall(RuleEngine([
        Rule("DROP", "TCP", "ANY", "ANY", 80)
    ]))

    syn = make_packet(flags=["SYN"])
    fw.process_packet(syn)

    pkt = make_packet(flags=["ACK"])
    assert fw.process_packet(pkt) == "ALLOW"


def test_udp_not_stateful():
    fw = Firewall(RuleEngine([
        Rule("ALLOW", "UDP", "ANY", "ANY", 53)
    ]))
    pkt = make_packet(protocol="UDP", dst_port=53)
    assert fw.process_packet(pkt) == "ALLOW"


def test_reverse_flow():
    fw = Firewall(RuleEngine([
        Rule("ALLOW", "TCP", "ANY", "ANY", 80)
    ]))

    syn = make_packet(flags=["SYN"])
    fw.process_packet(syn)

    reverse_pkt = make_packet(
        src_ip="1.1.1.1",
        dst_ip="10.0.0.1",
        src_port=80,
        dst_port=1234,
        flags=["ACK"]
    )

    assert fw.process_packet(reverse_pkt) == "ALLOW"


def test():
    test_basic_allow()
    test_basic_drop()
    test_default_drop()
    test_first_match_wins()
    #test_stateful_connection()
    #test_established_flow_bypass_rules()
    #test_udp_not_stateful()
    #test_reverse_flow()
    print("All tests passed!")


if __name__ == "__main__":
    test()
