"""
Test cases for the Firewall Filter FSM.
Each test case is a dictionary containing:
  - 'name': A description of the scenario.
  - 'packet': A list of hex bytes representing the packet.
  - 'expected': A dictionary of the expected 1-bit outputs (accept, drop, invalid).
"""

test_cases = [
    # ==========================================
    # ACCEPT SCENARIOS
    # ==========================================
    {
        "name": "ACCEPT: Valid PING packet",
        # SOF(AA), SRC(05), DST(10), TYPE(02), LEN(00), CHK(17)
        "packet": [0xAA, 0x05, 0x10, 0x02, 0x00, 0x17],
        "expected": {"accept": 1, "drop": 0, "invalid": 0}
    },
    {
        "name": "ACCEPT: Valid PING packet 2 (Different SRC/DST)",
        # SOF(AA), SRC(02), DST(20), TYPE(02), LEN(00), CHK(20)
        "packet": [0xAA, 0x02, 0x20, 0x02, 0x00, 0x20],
        "expected": {"accept": 1, "drop": 0, "invalid": 0}
    },
    {
        "name": "ACCEPT: Valid PING packet 3 (Another valid DST)",
        # SOF(AA), SRC(88), DST(30), TYPE(02), LEN(00), CHK(BA)
        "packet": [0xAA, 0x88, 0x30, 0x02, 0x00, 0xBA],
        "expected": {"accept": 1, "drop": 0, "invalid": 0}
    },
    {
        "name": "ACCEPT: Valid PING packet 4 (Max SRC)",
        # SOF(AA), SRC(FF), DST(10), TYPE(02), LEN(00), CHK(ED)
        "packet": [0xAA, 0xFF, 0x10, 0x02, 0x00, 0xED],
        "expected": {"accept": 1, "drop": 0, "invalid": 0}
    },
    {
        "name": "ACCEPT: Valid DATA packet",
        # SOF(AA), SRC(05), DST(20), TYPE(01), LEN(02), PAYLOAD(11, 22), CHK(15)
        "packet": [0xAA, 0x05, 0x20, 0x01, 0x02, 0x11, 0x22, 0x15],
        "expected": {"accept": 1, "drop": 0, "invalid": 0}
    },
    {
        "name": "ACCEPT: Valid DATA packet 2 (LEN=1)",
        # SOF(AA), SRC(03), DST(30), TYPE(01), LEN(01), PAYLOAD(AA), CHK(99)
        "packet": [0xAA, 0x03, 0x30, 0x01, 0x01, 0xAA, 0x99],
        "expected": {"accept": 1, "drop": 0, "invalid": 0}
    },
    {
        "name": "ACCEPT: Valid DATA packet 3 (LEN=3)",
        # SOF(AA), SRC(04), DST(10), TYPE(01), LEN(03), PAYLOAD(01, 02, 03), CHK(16)
        "packet": [0xAA, 0x04, 0x10, 0x01, 0x03, 0x01, 0x02, 0x03, 0x16],
        "expected": {"accept": 1, "drop": 0, "invalid": 0}
    },
    {
        "name": "ACCEPT: Valid DATA packet 4 (LEN=8 Max Payload)",
        # SOF(AA), SRC(12), DST(20), TYPE(01), LEN(08), PAYLOAD(01..08), CHK(33)
        "packet": [0xAA, 0x12, 0x20, 0x01, 0x08, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x33],
        "expected": {"accept": 1, "drop": 0, "invalid": 0}
    },
    {
        "name": "ACCEPT: Valid CONTROL packet (from admin)",
        # SOF(AA), SRC(01), DST(30), TYPE(03), LEN(01), PAYLOAD(FF), CHK(CC)
        "packet": [0xAA, 0x01, 0x30, 0x03, 0x01, 0xFF, 0xCC],
        "expected": {"accept": 1, "drop": 0, "invalid": 0}
    },
    {
        "name": "ACCEPT: Valid CONTROL packet 2 (No payload)",
        # SOF(AA), SRC(01), DST(10), TYPE(03), LEN(00), CHK(12)
        "packet": [0xAA, 0x01, 0x10, 0x03, 0x00, 0x12],
        "expected": {"accept": 1, "drop": 0, "invalid": 0}
    },
    {
        "name": "ACCEPT: Valid CONTROL packet 3 (Multiple payload bytes)",
        # SOF(AA), SRC(01), DST(20), TYPE(03), LEN(02), PAYLOAD(AA, 55), CHK(DF)
        "packet": [0xAA, 0x01, 0x20, 0x03, 0x02, 0xAA, 0x55, 0xDF],
        "expected": {"accept": 1, "drop": 0, "invalid": 0}
    },
    {
        "name": "ACCEPT: Valid CONTROL packet 4 (Max payload bytes)",
        # SOF(AA), SRC(01), DST(30), TYPE(03), LEN(08), PAYLOAD(FFx8), CHK(3A)
        "packet": [0xAA, 0x01, 0x30, 0x03, 0x08, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x3A],
        "expected": {"accept": 1, "drop": 0, "invalid": 0}
    },

    # ==========================================
    # INVALID SCENARIOS (Format Violations)
    # ==========================================
    {
        "name": "INVALID: Incorrect SOF byte",
        # SOF(BB - WRONG), SRC(05), DST(10), TYPE(02), LEN(00), CHK(17)
        "packet": [0xBB, 0x05, 0x10, 0x02, 0x00, 0x17],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: Incorrect SOF byte 2",
        # SOF(00 - WRONG), SRC(05), DST(10), TYPE(02), LEN(00), CHK(17)
        "packet": [0x00, 0x05, 0x10, 0x02, 0x00, 0x17],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: Incorrect SOF byte 3",
        # SOF(FF - WRONG), SRC(05), DST(10), TYPE(02), LEN(00), CHK(17)
        "packet": [0xFF, 0x05, 0x10, 0x02, 0x00, 0x17],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: Incorrect SOF byte 4",
        # SOF(A0 - WRONG), SRC(05), DST(10), TYPE(02), LEN(00), CHK(17)
        "packet": [0xA0, 0x05, 0x10, 0x02, 0x00, 0x17],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: Unknown Packet Type",
        # SOF(AA), SRC(05), DST(10), TYPE(04 - WRONG), LEN(00), CHK(11)
        "packet": [0xAA, 0x05, 0x10, 0x04, 0x00, 0x11],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: Unknown Packet Type 2 (0x00)",
        # SOF(AA), SRC(05), DST(10), TYPE(00 - WRONG), LEN(00), CHK(15)
        "packet": [0xAA, 0x05, 0x10, 0x00, 0x00, 0x15],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: Unknown Packet Type 3 (0xFF)",
        # SOF(AA), SRC(05), DST(10), TYPE(FF - WRONG), LEN(00), CHK(EA)
        "packet": [0xAA, 0x05, 0x10, 0xFF, 0x00, 0xEA],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: Unknown Packet Type 4 (0x05)",
        # SOF(AA), SRC(05), DST(10), TYPE(05 - WRONG), LEN(00), CHK(10)
        "packet": [0xAA, 0x05, 0x10, 0x05, 0x00, 0x10],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: Payload length > 8",
        # SOF(AA), SRC(05), DST(10), TYPE(01), LEN(09 - WRONG), PAYLOAD(1..9), CHK(1C)
        "packet": [0xAA, 0x05, 0x10, 0x01, 0x09, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x1C],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: Payload length > 8 (LEN=10)",
        # SOF(AA), SRC(05), DST(10), TYPE(01), LEN(0A - WRONG), PAYLOAD(10x 00), CHK(1E)
        "packet": [0xAA, 0x05, 0x10, 0x01, 0x0A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1E],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: Payload length > 8 (LEN=11)",
        # SOF(AA), SRC(05), DST(10), TYPE(01), LEN(0B - WRONG), PAYLOAD(11x 00), CHK(1F)
        "packet": [0xAA, 0x05, 0x10, 0x01, 0x0B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: Payload length > 8 (LEN=12)",
        # SOF(AA), SRC(05), DST(10), TYPE(01), LEN(0C - WRONG), PAYLOAD(12x 00), CHK(18)
        "packet": [0xAA, 0x05, 0x10, 0x01, 0x0C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x18],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: PING packet with payload",
        # SOF(AA), SRC(05), DST(10), TYPE(02), LEN(01 - WRONG), PAYLOAD(00), CHK(16)
        "packet": [0xAA, 0x05, 0x10, 0x02, 0x01, 0x00, 0x16],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: PING packet with payload 2 (LEN=2)",
        # SOF(AA), SRC(05), DST(10), TYPE(02), LEN(02 - WRONG), PAYLOAD(00, 00), CHK(15)
        "packet": [0xAA, 0x05, 0x10, 0x02, 0x02, 0x00, 0x00, 0x15],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: PING packet with payload 3 (LEN=8)",
        # SOF(AA), SRC(05), DST(10), TYPE(02), LEN(08 - WRONG), PAYLOAD(8x 00), CHK(1F)
        "packet": [0xAA, 0x05, 0x10, 0x02, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x1F],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: PING packet with payload 4 (LEN=1, PAYLOAD=FF)",
        # SOF(AA), SRC(05), DST(10), TYPE(02), LEN(01 - WRONG), PAYLOAD(FF), CHK(E9)
        "packet": [0xAA, 0x05, 0x10, 0x02, 0x01, 0xFF, 0xE9],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: DATA packet without payload",
        # SOF(AA), SRC(05), DST(10), TYPE(01), LEN(00 - WRONG), CHK(14)
        "packet": [0xAA, 0x05, 0x10, 0x01, 0x00, 0x14],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: DATA packet without payload 2",
        # SOF(AA), SRC(02), DST(20), TYPE(01), LEN(00 - WRONG), CHK(23)
        "packet": [0xAA, 0x02, 0x20, 0x01, 0x00, 0x23],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: DATA packet without payload 3",
        # SOF(AA), SRC(88), DST(30), TYPE(01), LEN(00 - WRONG), CHK(B9)
        "packet": [0xAA, 0x88, 0x30, 0x01, 0x00, 0xB9],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: DATA packet without payload 4",
        # SOF(AA), SRC(FF), DST(10), TYPE(01), LEN(00 - WRONG), CHK(EE)
        "packet": [0xAA, 0xFF, 0x10, 0x01, 0x00, 0xEE],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: Checksum mismatch",
        # SOF(AA), SRC(05), DST(10), TYPE(02), LEN(00), CHK(00 - WRONG, should be 17)
        "packet": [0xAA, 0x05, 0x10, 0x02, 0x00, 0x00],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: Checksum mismatch 2",
        # SOF(AA), SRC(05), DST(10), TYPE(02), LEN(00), CHK(18 - WRONG, should be 17)
        "packet": [0xAA, 0x05, 0x10, 0x02, 0x00, 0x18],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: Checksum mismatch 3",
        # SOF(AA), SRC(05), DST(10), TYPE(02), LEN(00), CHK(FF - WRONG, should be 17)
        "packet": [0xAA, 0x05, 0x10, 0x02, 0x00, 0xFF],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },
    {
        "name": "INVALID: Checksum mismatch 4 (DATA packet)",
        # SOF(AA), SRC(05), DST(20), TYPE(01), LEN(02), PAYLOAD(11, 22), CHK(00 - WRONG, should be 15)
        "packet": [0xAA, 0x05, 0x20, 0x01, 0x02, 0x11, 0x22, 0x00],
        "expected": {"accept": 0, "drop": 0, "invalid": 1}
    },

    # ==========================================
    # DROP SCENARIOS (Policy Violations)
    # ==========================================
    {
        "name": "DROP: Blocked source address (0xE0)",
        # SOF(AA), SRC(E0 - BLOCKED), DST(10), TYPE(02), LEN(00), CHK(F2)
        "packet": [0xAA, 0xE0, 0x10, 0x02, 0x00, 0xF2],
        "expected": {"accept": 0, "drop": 1, "invalid": 0}
    },
    {
        "name": "DROP: Blocked source address (0xE0) 2 - DATA packet",
        # SOF(AA), SRC(E0 - BLOCKED), DST(20), TYPE(01), LEN(01), PAYLOAD(AA), CHK(6A)
        "packet": [0xAA, 0xE0, 0x20, 0x01, 0x01, 0xAA, 0x6A],
        "expected": {"accept": 0, "drop": 1, "invalid": 0}
    },
    {
        "name": "DROP: Blocked source address (0xE0) 3 - PING to DST 20",
        # SOF(AA), SRC(E0 - BLOCKED), DST(20), TYPE(02), LEN(00), CHK(C2)
        "packet": [0xAA, 0xE0, 0x20, 0x02, 0x00, 0xC2],
        "expected": {"accept": 0, "drop": 1, "invalid": 0}
    },
    {
        "name": "DROP: Blocked source address (0xE0) 4 - DATA to DST 30",
        # SOF(AA), SRC(E0 - BLOCKED), DST(30), TYPE(01), LEN(02), PAYLOAD(00, 00), CHK(D3)
        "packet": [0xAA, 0xE0, 0x30, 0x01, 0x02, 0x00, 0x00, 0xD3],
        "expected": {"accept": 0, "drop": 1, "invalid": 0}
    },
    {
        "name": "DROP: Blocked source address (0xE1)",
        # SOF(AA), SRC(E1 - BLOCKED), DST(10), TYPE(02), LEN(00), CHK(F3)
        "packet": [0xAA, 0xE1, 0x10, 0x02, 0x00, 0xF3],
        "expected": {"accept": 0, "drop": 1, "invalid": 0}
    },
    {
        "name": "DROP: Blocked source address (0xE1) 2 - PING to DST 20",
        # SOF(AA), SRC(E1 - BLOCKED), DST(20), TYPE(02), LEN(00), CHK(C3)
        "packet": [0xAA, 0xE1, 0x20, 0x02, 0x00, 0xC3],
        "expected": {"accept": 0, "drop": 1, "invalid": 0}
    },
    {
        "name": "DROP: Blocked source address (0xE1) 3 - DATA to DST 30",
        # SOF(AA), SRC(E1 - BLOCKED), DST(30), TYPE(01), LEN(01), PAYLOAD(FF), CHK(2E)
        "packet": [0xAA, 0xE1, 0x30, 0x01, 0x01, 0xFF, 0x2E],
        "expected": {"accept": 0, "drop": 1, "invalid": 0}
    },
    {
        "name": "DROP: Blocked source address (0xE1) 4 - PING to DST 30",
        # SOF(AA), SRC(E1 - BLOCKED), DST(30), TYPE(02), LEN(00), CHK(D3)
        "packet": [0xAA, 0xE1, 0x30, 0x02, 0x00, 0xD3],
        "expected": {"accept": 0, "drop": 1, "invalid": 0}
    },
    {
        "name": "DROP: Disallowed destination address",
        # SOF(AA), SRC(05), DST(40 - DISALLOWED), TYPE(02), LEN(00), CHK(47)
        "packet": [0xAA, 0x05, 0x40, 0x02, 0x00, 0x47],
        "expected": {"accept": 0, "drop": 1, "invalid": 0}
    },
    {
        "name": "DROP: Disallowed destination address 2 (0x00)",
        # SOF(AA), SRC(05), DST(00 - DISALLOWED), TYPE(02), LEN(00), CHK(07)
        "packet": [0xAA, 0x05, 0x00, 0x02, 0x00, 0x07],
        "expected": {"accept": 0, "drop": 1, "invalid": 0}
    },
    {
        "name": "DROP: Disallowed destination address 3 (0xFF)",
        # SOF(AA), SRC(05), DST(FF - DISALLOWED), TYPE(01), LEN(01), PAYLOAD(00), CHK(FA)
        "packet": [0xAA, 0x05, 0xFF, 0x01, 0x01, 0x00, 0xFA],
        "expected": {"accept": 0, "drop": 1, "invalid": 0}
    },
    {
        "name": "DROP: Disallowed destination address 4 (0x41)",
        # SOF(AA), SRC(05), DST(41 - DISALLOWED), TYPE(02), LEN(00), CHK(46)
        "packet": [0xAA, 0x05, 0x41, 0x02, 0x00, 0x46],
        "expected": {"accept": 0, "drop": 1, "invalid": 0}
    },
    {
        "name": "DROP: Unauthorized CONTROL packet",
        # SOF(AA), SRC(05 - NOT ADMIN), DST(10), TYPE(03), LEN(00), CHK(16)
        "packet": [0xAA, 0x05, 0x10, 0x03, 0x00, 0x16],
        "expected": {"accept": 0, "drop": 1, "invalid": 0}
    },
    {
        "name": "DROP: Unauthorized CONTROL packet 2",
        # SOF(AA), SRC(02 - NOT ADMIN), DST(10), TYPE(03), LEN(00), CHK(11)
        "packet": [0xAA, 0x02, 0x10, 0x03, 0x00, 0x11],
        "expected": {"accept": 0, "drop": 1, "invalid": 0}
    },
    {
        "name": "DROP: Unauthorized CONTROL packet 3",
        # SOF(AA), SRC(FF - NOT ADMIN), DST(20), TYPE(03), LEN(01), PAYLOAD(AA), CHK(77)
        "packet": [0xAA, 0xFF, 0x20, 0x03, 0x01, 0xAA, 0x77],
        "expected": {"accept": 0, "drop": 1, "invalid": 0}
    },
    {
        "name": "DROP: Unauthorized CONTROL packet 4",
        # SOF(AA), SRC(10 - NOT ADMIN), DST(30), TYPE(03), LEN(00), CHK(23)
        "packet": [0xAA, 0x10, 0x30, 0x03, 0x00, 0x23],
        "expected": {"accept": 0, "drop": 1, "invalid": 0}
    }
]

if __name__ == "__main__":
    # Simple utility to dump the amount of tests
    print(f"Loaded {len(test_cases)} Firewall FSM test scenarios.")