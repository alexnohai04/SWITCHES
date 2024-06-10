import dns.resolver
import base64

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

    # Decodificare base64
    try:
        file_data = base64.b64decode(file_data)
    except Exception as e:
        print(f"Error decoding base64 data: {e}")
        return

   
    print(f"Total file data received: {file_data}")
    with open('received_file', 'wb') as f:
        f.write(file_data)
    print("File received successfully")

# Utilizează localhost pentru testare inițială
query_file("127.0.0.1", "www.switches.systems")

