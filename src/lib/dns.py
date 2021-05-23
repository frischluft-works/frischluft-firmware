# This class implements a small DNS server for Captive Portal redirects
# found somewhere on the internet, TODO: needs credits.

class DNSQuery:
    def __init__(self, data):
        self.data = data
        self.domain = ''
        tipo = (data[2] >> 3) & 15  # Opcode bits
        if tipo == 0:  # Standard query
            ini = 12
            lon = data[ini]
            while lon != 0:
                self.domain += data[ini + 1:ini + lon + 1].decode('utf-8') + '.'
                ini += lon + 1
                lon = data[ini]
        # print("DNSQuery domain:" + self.domain)

    def response(self, ip):
        # print("DNSQuery response: {} ==> {}".format(self.domain, ip))
        if self.domain:
            packet = self.data[:2] + b'\x81\x80'
            packet += self.data[4:6] + self.data[4:6] + b'\x00\x00\x00\x00'  # Questions and Answers Counts
            packet += self.data[12:]  # Original Domain Name Question
            packet += b'\xC0\x0C'  # Pointer to domain name
            packet += b'\x00\x01\x00\x01\x00\x00\x00\x3C\x00\x04'  # Response type, ttl and resource data length -> 4 bytes
            packet += bytes(map(int, ip.split('.')))  # 4bytes of IP
        # print(packet)
        return packet
