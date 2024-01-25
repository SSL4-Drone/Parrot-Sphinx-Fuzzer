import pyshark

class PacketParser:
    def __init__(self, iface, seq):
        self.iface = iface
        self.seq = seq
    
    def packet_check(self, packet):
        if 'IP' in packet:
            # UDP packet이고 drone ip가 보낸 packet인지 체크
            if packet.ip.proto == '17' and packet.ip.src == "192.168.42.1":
                pay = packet.udp.payload
                
                # data가 01로 시작하는지, sequence num 체크
                if pay.startswith('01:8b') and pay.endswith(hex(self.seq)[2:]):
                    return True
                

    def parsing(self):
        capture = pyshark.LiveCapture(interface=self.iface)
        for packet in capture.sniff_continuously(packet_count=100):
            if self.packet_check(packet):
                return packet.udp.payload


# parser = PacketParser("Wi-Fi", 43)
# payload = parser.parsing()
# print(payload)
