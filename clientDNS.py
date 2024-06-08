import dns.resolver

def query_file(server, domain):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [server]
    query_name = f"{domain}.tunel.live."
    file_data = b''
    
    while True:
        try:
            answers = resolver.resolve(query_name, 'TXT')
            for answer in answers:
                chunk = answer.to_text().strip('"').encode()
                file_data += chunk
            break
        except dns.exception.DNSException as e:
            print(f"Failed to retrieve chunk: {e}")
            break
    
    with open('received_file', 'wb') as f:
        f.write(file_data)
    print("File received successfully")

query_file("your.dns.server.ip", "examplefile")

