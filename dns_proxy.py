import socket
from dnslib import DNSRecord, DNSHeader
import configparser

PORT = 53

# DNSリクエストを複数のアップストリームに投げて帰ってきた応答をクライアントに返す
def handle_dns_request(data, addr, servers):
    request = DNSRecord.parse(data)
    print(f"Received request from {addr} for {request.q.qname}")

    # 応答を格納するリスト
    responses = []

    # 各サーバにリクエストを送信
    for server in servers:
        response = send_request_to_server(server, data)
        if response:
            response_record = DNSRecord.parse(response)
            print(f"Response from {server}.")
 
            responses.append(response)

    # 最初の応答をクライアントに返す
    if responses:
        return responses[0]
    else:
        return None

# リクエストを送信して応答待機して応答が返ってきたら戻す
def send_request_to_server(server, data):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(2)  # タイムアウト設定
        sock.sendto(data, (server, PORT))
        response, _ = sock.recvfrom(1410)  # 最大1410バイトの応答を受け取る
        return response
    except Exception as e:
        print(f"Error communicating with {server}: {e}")
        return None

# server.confを読み込む関数
def load_servers_from_conf(file_path):
    servers = []
    config = configparser.ConfigParser()
    config.read(file_path)

    for section in config.sections():
        for key, value in config.items(section):
            servers.append(value.strip()) #IPアドレス

    return servers

def main():
    # server.confからIPアドレスを読み込む
    servers = load_servers_from_conf('server.conf')

    # port53のlisten
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', PORT))

    print(f"Listening for DNS requests on port {PORT}...")
    while True:
        # 最大1410バイトのリクエストを受信(EDNS考慮)
        request, addr = sock.recvfrom(1410)  
        # requestをserversに投げる addr(クライアントのIPアドレス)は通知用
        response = handle_dns_request(request, addr, servers) 

        # responseを受け取ったらaddrに返す
        if response:
            sock.sendto(response, addr)  # クライアントに応答を返す

if __name__ == "__main__":
    main()
