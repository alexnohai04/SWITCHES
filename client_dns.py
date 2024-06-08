import dns.resolver

def query_file(server, domain):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [server]
    query_name = f"{domain}.tunel.live."
    file_data = b''

    while True:
        try:
            print(f"Sending query for: {query_name}")
            answers = resolver.resolve(query_name, 'TXT')
            for answer in answers:
                chunk = answer.to_text().strip('"').encode('latin1')
                print(f"Received chunk: {chunk}")
                file_data += chunk
            break
        except dns.exception.DNSException as e:
            print(f"Failed to retrieve chunk: {e}")
            break

    # Eliminare secvență de escape specifică și caractere de control
    file_data = file_data.replace(b'\\010', b'').replace(b'\\n', b'\n').rstrip()

    # Adaugă newline la finalul fișierului
    file_data += b'\n'

    print(f"Total file data received: {file_data}")
    with open('received_file', 'wb') as f:
        f.write(file_data)
    print("File received successfully")

# Utilizează localhost pentru testare inițială
query_file("127.0.0.1", "www.switches.systems")

