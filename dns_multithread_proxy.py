import socket # 送受信用
from dnslib import DNSRecord, DNSHeader, QTYPE, CLASS # ログ出力用
import logging # ログ出力用
import threading # マルチスレッド処理用
import configparser # コンフィグ
import time # 実行時間計測用

PORT = 53
LOG_FILE = "logfile.log"

logging.basicConfig(
    filename=LOG_FILE, 
    level=logging.INFO, 
    format='%(asctime)s - %(message)s',
    datefmt='%b %d %H:%M:%S' # 一応Unboundと同じフォーマット
)

# server.confを読み込む関数
def load_servers_from_conf(file_path):
    servers = []
    config = configparser.ConfigParser()
    config.read(file_path)

    for section in config.sections():
        for key, value in config.items(section):
            servers.append(value.strip()) #IPアドレス

    return servers

# ドメイン名とレコードタイプ、クラスを取得する
def parse_dns_query(data):
    dns_record = DNSRecord.parse(data)
    # クエリのドメイン名を取得
    domain_name = str(dns_record.q.qname)

    # dnslibのマッピング(qxxxで数字が取得される)
    record_type = QTYPE[dns_record.q.qtype]
    record_class = CLASS[dns_record.q.qclass]

    return domain_name, record_type, record_class

# DNSリクエストをアップストリームに投げて帰ってきた応答をクライアントに返す
def handle_dns_request(data, server, responses):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(1)  # タイムアウト設定
            logging.info(f"Duplicating and sending request query to {server}") # neko1とかneko2になげる
            sock.sendto(data, (server, PORT))
            response, addr = sock.recvfrom(1410)  # 最大1410バイトの応答を受け取る
            logging.info(f"Received answer query to {server}")

            # responseに格納
            responses.append(response)
            on_received = True

    except Exception as e:
        logging.info(f"Error communicating with {server}: {e}")

# クエリを受け取った後の処理
def dns_query(sock, addr, request, servers):
    source_ip = addr[0]
    responses = []
    # 処理時間計測用
    start = time.perf_counter()

    logging.info(f"Received request query from client({source_ip})")
    # requestをserversに投げる
    handle_threads = [0 for _ in servers]
    for i in range(len(servers)):
        handle_threads[i] = threading.Thread(target=handle_dns_request, args=(request, servers[i], responses), name=str(i))
        handle_threads[i].start()

    #応答が買ってくるまで待機し、他はstartして投げっぱなしにする
    handle_threads[0].join()
    logging.info(f"Sending answer query to client({source_ip})")
    if responses == []:
        logging.info(f"Response nothing")
    else:
        sock.sendto(responses[0], addr)

    # パースして各情報を取得
    domain_name, record_type, record_class = parse_dns_query(request)
    logging.info(f"{source_ip} {domain_name} {record_type} {record_class}")
    responses = []

    end = time.perf_counter()
    print(str(round((end-start)*1000, 3)) + "ms")

def main():
    # server.confからIPアドレスを読み込む
    servers = load_servers_from_conf('server.conf')
    query_threads = []

    # portのlisten
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', PORT))

    logging.info(f"Listening for DNS requests on port {PORT}...")
    while True:
        # 最大1410バイトのリクエストを受信(EDNS考慮)
        request, addr = sock.recvfrom(1410)  # addrは(ip, port)の形式

        source_ip = addr[0]
        query_threads.append(threading.Thread(target=dns_query, args=(sock, addr, request, servers)))
        query_threads[-1].start()

if __name__ == "__main__":
    main()
