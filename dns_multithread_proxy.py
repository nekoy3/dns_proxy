import socket
from dnslib import DNSRecord, DNSHeader
import threading
import queue
import configparser

PORT = 53
LOG_FILE = "latest.log"
# ログ出力用
def log_output(text):
    print(text)

# server.confを読み込む関数
def load_servers_from_conf(file_path):
    servers = []
    config = configparser.ConfigParser()
    config.read(file_path)

    for section in config.sections():
        for key, value in config.items(section):
            servers.append(value.strip()) #IPアドレス

    return servers

# DNSリクエストをアップストリームに投げて帰ってきた応答をクライアントに返す
def handle_dns_request(data, server, responses):
    log_output(server)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(2)  # タイムアウト設定
            sock.sendto(data, (server, PORT))
            response, _ = sock.recvfrom(1410)  # 最大1410バイトの応答を受け取る

            # responseに格納
            responses.append(response)

    except Exception as e:
        print(f"Error communicating with {server}: {e}")

def main():
    # server.confからIPアドレスを読み込む
    servers = load_servers_from_conf('server.conf')
    responses = []

    # portのlisten
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', PORT))

    print(f"Listening for DNS requests on port {PORT}...")
    while True:
        # 最大1410バイトのリクエストを受信(EDNS考慮)
        request, addr = sock.recvfrom(1410)  
        # requestをserversに投げる
        threads = [0 for _ in servers]
        for i in range(len(servers)):
            threads[i] = threading.Thread(target=handle_dns_request, args=(request, servers[i], responses), name=str(i))

        #処理開始
        for i in range(len(threads)):
            threads[i].start()
        
        """
        threadそれぞれからresponseを受け取って初回はクライアントに応答を返し、それ以降は受け取るだけで使わず放置する感じにする
        """
        #それぞれの応答を待機してaddrに応答を返す
        for i in range(len(threads)):
            threads[i].join()
            if responses == [] or i >= 1:
                continue
            sock.sendto(responses[0], addr)
        responses = []

if __name__ == "__main__":
    main()
