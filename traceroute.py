import socket
import traceback
import requests

# Socket de UDP
udp_send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, proto=socket.IPPROTO_UDP)

# Socket RAW de citire a răspunsurilor ICMP
icmp_recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
icmp_recv_socket.settimeout(3)

def get_ip_location(ip):
    try:
        response = requests.get(f'https://ipinfo.io/{ip}/json')
        data = response.json()
        return data.get('city', 'Unknown'), data.get('region', 'Unknown'), data.get('country', 'Unknown')
    except Exception as e:
        print(f"Could not get location for IP {ip}: {e}")
        return 'Unknown', 'Unknown', 'Unknown'

def traceroute(ip, port):
    max_hops = 10
    results = []
    for ttl in range(1, max_hops + 1):
        udp_send_sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
        udp_send_sock.sendto(b'salut', (ip, port))

        try:
            data, addr = icmp_recv_socket.recvfrom(63535)
            addr = addr[0]
            if addr:
                city, region, country = get_ip_location(addr)
                results.append((ttl, addr, city, region, country))
                print(f"{ttl}\t{addr}\t{city}\t{region}\t{country}")
                if addr == ip:
                    print("Reached destination.")
                    break
            else:
                results.append((ttl, '*', 'Request timed out.', '', ''))
                print(f"{ttl}\t*\tRequest timed out.")
        except socket.timeout:
            results.append((ttl, '*', 'Request timed out.', '', ''))
            print(f"{ttl}\t*\tRequest timed out.")
        except Exception as e:
            print(f"Error: {e}")
            print(traceback.format_exc())
    return results

def save_results(filename, results):
    with open(filename, 'w') as f:
        for ttl, ip, city, region, country in results:
            f.write(f"{ttl}\t{ip}\t{city}\t{region}\t{country}\n")

if __name__ == "__main__":
    sites = {
        'Google': '8.8.8.8',
        'China': 'www.baidu.cn',
        'South_Africa': 'www.gov.za',
        'Australia': 'www.gov.au'
    }

    for name, ip in sites.items():
        print(f"Tracing route to {name} ({ip})")
        results = traceroute(ip, 33434)
        save_results(f"{name}_traceroute.txt", results)

