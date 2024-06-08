from scapy.all import *
import socket

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

def read_file_in_chunks(filename, chunk_size=255):
    try:
        with open(filename, 'rb') as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                yield chunk
    except FileNotFoundError:
        return [b"File not found"]

while True:
    print("Aștept cereri DNS...")
    request, adresa_sursa = simple_udp.recvfrom(65535)
    print(f"Cerere primită de la {adresa_sursa}")
    packet = DNS(request)
    dns = packet.getlayer(DNS)

    if dns is not None and dns.opcode == 0:  # DNS QUERY
        qname = dns.qd.qname
        print(f"Received query for: {qname}")

        if qname in dns_records:
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
            print('Sending response:')
            print(dns_response.summary())
            simple_udp.sendto(bytes(dns_response), adresa_sursa)
        elif qname.endswith(b'.tunel.live.'):
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
        else:
            print(f"No record found for: {qname}")

simple_udp.close()

