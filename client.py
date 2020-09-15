import argparse
import socket
from math import ceil
from pathlib import Path

from tqdm import trange

FILENAME_PREFIX = "qdjwnanxlA912enAS:"
BUFFER_SIZE = 1024


def send_filename(sock, path):
    sock.send((FILENAME_PREFIX + path.name).encode())


def send_file(sock, path):
    filesize = path.stat().st_size
    buffer = path.read_bytes()
    num_transfers = ceil(filesize / BUFFER_SIZE)
    idx = 0
    for i in trange(num_transfers):
        sock.send(buffer[idx : idx + BUFFER_SIZE])
        idx += BUFFER_SIZE


def connect(host, port):
    sock = socket.socket()
    sock.connect((host, port))

    return sock


def disconnect(sock):
    sock.shutdown(socket.SHUT_WR)


def get_cli_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("filename")
    parser.add_argument("host")
    parser.add_argument("port", type=int)

    return parser.parse_args()


if __name__ == "__main__":
    cli_args = get_cli_args()
    sock = connect(cli_args.host, cli_args.port)

    path = Path(cli_args.filename)
    send_filename(sock, path)
    send_file(sock, path)

    disconnect(sock)
