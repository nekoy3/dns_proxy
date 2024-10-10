import socket
from dnslib import DNSRecord, DNSHeader
import configparser

PORT = 53

# server.confを読み込む関数
def load_servers_from_conf(file_path):
    servers = []
    config = configparser.ConfigParser()
    config.read(file_path)

    for section in config.sections():
        for key, value in config.items(section):
            servers.append(value.strip()) #IPアドレス

    return servers

# DNSリクエストを複数のアップストリームに投げて帰ってきた応答をクライアントに返す
def handle_dns_request(data, servers):
    responses = []
    # 各サーバにリクエストを送信
    for server in servers:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(2)  # タイムアウト設定
                sock.sendto(data, (server, PORT))
                response, _ = sock.recvfrom(1410)  # 最大1410バイトの応答を受け取る
                responses.append(response)

        except Exception as e:
            print(f"Error communicating with {server}: {e}")

    # 応答を全てクライアントに返す
    if responses:
        return responses
    else:
        return None

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
        # requestをserversに投げて帰ってきたresponsesを受け取る
        responses = handle_dns_request(request, servers) 

        # responsesを全てaddrに返す
        for response in responses:
            sock.sendto(response, addr)  # クライアントに応答を返す

if __name__ == "__main__":
    main()
