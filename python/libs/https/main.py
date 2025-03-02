#!/bin/python3
"""
Python script for running a local development server.
Default password encryption password: 1234
"""

import os
import ssl
import argparse
import http.server

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port",
        "-p",
        type=int,
        default=8000,
        help="Which port to run the server on.",
    )
    args = parser.parse_args()
    lib_path = os.path.dirname(os.path.abspath(__file__))
    cert_path = os.path.join(lib_path, "cert.pem")
    key_path = os.path.join(lib_path, "key.pem")

    host = "127.0.0.1"
    port = 8000 if not args.port else args.port
    httpd = http.server.HTTPServer((host, port), http.server.SimpleHTTPRequestHandler)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile=cert_path, keyfile=key_path)

    httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    print(f"HTTPS server started @ https://127.0.0.1:{port}")
    httpd.serve_forever()
