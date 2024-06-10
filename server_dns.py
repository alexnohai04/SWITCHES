import socket
import signal
import sys
import base64
from scapy.all import *

# Configurare server DNS
simple_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)
simple_udp.bind(('0.0.0.0', 53))
print("Server DNS pornit și ascultă pe portul 53...")

# Dicționar cu înregistrările DNS
dns_records = {
    b'switches.systems.': '109.166.134.225',
    b'www.switches.systems.': '109.166.134.225',
    b'ns1.switches.systems.': '109.166.134.225',
    b'ns2.switches.systems.': '109.166.134.225'
}

# Dicționar cu înregistrările NS
ns_records = {
    b'switches.systems.': [b'ns1.switches.systems.', b'ns2.switches.systems.'],
    b'tunel.live.': [b'ns1.tunel.live.', b'ns2.tunel.live.']
}

def read_file_in_chunks(filename, chunk_size=255):
    try:
        with open(filename, 'rb') as file:
            encoded_data = base64.b64encode(file.read())
            for i in range(0, len(encoded_data), chunk_size):
                yield encoded_data[i:i+chunk_size]
    except FileNotFoundError:
        return [b"File not found"]

def handle_sigint(signal, frame):
    print("\nServer DNS oprit.")
    simple_udp.close()
    sys.exit(0)

# Capturarea semnalului Ctrl+C
signal.signal(signal.SIGINT, handle_sigint)

while True:
    print("Aștept cereri DNS...")
    try:
        request, adresa_sursa = simple_udp.recvfrom(65535)
        print(f"Cerere primită de la {adresa_sursa}")
        packet = DNS(request)
        dns = packet.getlayer(DNS)

        if dns is not None and dns.opcode == 0:  # DNS QUERY
            qname = dns.qd.qname
            qtype = dns.qd.qtype
            print(f"Received query for: {qname} of type {qtype}")

            if qtype == 1 and qname in dns_records:  # A record
                dns_answer = DNSRR(
                    rrname=qname,
                    ttl=330,
                    type="A",
                    rclass="IN",
                    rdata=dns_records[qname]
                )

                dns_response = DNS(
                    id=packet[DNS].id,
                    qr=1,
                    aa=1,
                    rcode=0,
                    qd=packet.qd,
                    an=dns_answer
                )
                print('Sending A record response:')
                print(dns_response.summary())
                simple_udp.sendto(bytes(dns_response), adresa_sursa)

            elif qtype == 16 and qname.endswith(b'.tunel.live.'):  # TXT record for file transfer
                filename = qname.split(b'.')[0].decode()
                print(f"Requested file: {filename}")
                chunks = read_file_in_chunks(filename)
                for chunk in chunks:
                    dns_answer = DNSRR(
                        rrname=qname,
                        ttl=330,
                        type="TXT",
                        rclass="IN",
                        rdata=chunk
                    )
                    dns_response = DNS(
                        id=packet[DNS].id,
                        qr=1,
                        aa=1,
                        rcode=0,
                        qd=packet.qd,
                        an=dns_answer
                    )
                    print(f'Sending file chunk: {chunk}')
                    simple_udp.sendto(bytes(dns_response), adresa_sursa)

            elif qtype == 2 and qname in ns_records:  # NS record
                ns_answers = []
                for ns in ns_records[qname]:
                    ns_answers.append(DNSRR(
                        rrname=qname,
                        ttl=330,
                        type="NS",
                        rclass="IN",
                        rdata=ns
                    ))

                dns_response = DNS(
                    id=packet[DNS].id,
                    qr=1,
                    aa=1,
                    rcode=0,
                    qd=packet.qd,
                    an=ns_answers[0],
                    ns=ns_answers
                )
                print('Sending NS record response:')
                for answer in ns_answers:
                    print(answer.summary())
                simple_udp.sendto(bytes(dns_response), adresa_sursa)

            else:
                print(f"No record found for: {qname} of type {qtype}")

    except Exception as e:
        print(f"An error occurred: {e}")

simple_udp.close()

