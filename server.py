import os
import selectors
import socket
from contextlib import suppress
from pathlib import Path

FILENAME_PREFIX = "qdjwnanxlA912enAS:"
BUFFER_SIZE = 1024
UPLOAD_DIR = Path("uploaded_files")


selector = selectors.DefaultSelector()
files = {}


def is_filename_received(data):
    return data.startswith(FILENAME_PREFIX.encode())


def get_filename(data):
    return data.decode().split(FILENAME_PREFIX)[1]


def open_file(filename, connection):
    path = UPLOAD_DIR / filename
    files[connection] = open(path, "wb")


def close_file(connection):
    with suppress(KeyError):
        f = files[connection]
        f.close()


def write_to_file(data, connection):
    files[connection].write(data)


def handle_data(data, connection):
    if is_filename_received(data):
        filename = get_filename(data)
        open_file(filename, connection)
    else:
        write_to_file(data, connection)


def accept(sock):
    connection, addr = sock.accept()

    connection.setblocking(False)
    selector.register(connection, selectors.EVENT_READ, read)


def read(connection):
    data = connection.recv(1024)

    if data:
        handle_data(data, connection)
    else:
        selector.unregister(connection)

        close_file(connection)
        connection.close()


if __name__ == "__main__":
    sock = socket.socket()
    sock.bind(("0.0.0.0", 1337))
    sock.listen()

    sock.setblocking(False)
    selector.register(sock, selectors.EVENT_READ, accept)

    while True:
        for key, _ in selector.select():
            callback = key.data
            callback(key.fileobj)
