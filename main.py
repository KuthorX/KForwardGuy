from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
import json
import os

ip = None
port = None
extra = None

class HTTPHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        message = """<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Message Send</title>
    <script src="https://cdn.jsdelivr.net/npm/qrcode-generator@1.4.4/qrcode.min.js"></script>
</head>

<body>
    <p>Server Addr <strong>%s:%s</strong></p>
    <p>Extra: %s</p>
    <textarea id="input_msg"></textarea>
    <button id="send">Send</button>
    <p>↓ Scan QR code to quickly enter this page ↓</p>
    <div id="qrcode"></div>
    
    <script>
    var create_qrcode = function(text, typeNumber,
          errorCorrectionLevel, mode, mb) {

          qrcode.stringToBytes = qrcode.stringToBytesFuncs[mb];

          var qr = qrcode(typeNumber || 4, errorCorrectionLevel || 'M');
          qr.addData(text, mode);
          qr.make();

          return qr.createImgTag();
      };
        window.onload = async function () {
            document.getElementById('qrcode').innerHTML =
                  create_qrcode('%s', '0', 'H', 'Byte', 'UTF-8');
            const button = document.getElementById("send")
            button.onclick = async function () {
                const input = document.getElementById("input_msg").value
                const send_data = { input }
                let response = await fetch('/send_msg', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json;charset=utf-8'
                    },
                    body: JSON.stringify(send_data)
                });
                let result = await response.json();
                alert(result.message);
            }
        }
    </script>
</body>

</html>
        """ % (ip, port, extra, f"http://{ip}:{port}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(message, "utf-8"))

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length"))
        post_body = self.rfile.read(content_len)
        print(json.loads(post_body.decode("utf-8"))["input"])
        self.send_response(200)
        self.send_header("Content-Type",
                         "application/json; charset=utf-8")
        self.end_headers()
        return_data = json.dumps({"message": "ok, please check server log"})
        self.wfile.write(bytes(return_data, "utf-8"))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-index", help="index of multi local ip", default="0")
    parser.add_argument("-extra", help="extra msg", default="")
    args = parser.parse_args()
    index = args.index
    extra = args.extra
    print(f'use index: {index}')
    print(f'use extra: {extra}')

    shell_get_ip = "ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'"
    shell_result = os.popen(shell_get_ip)
    ip = shell_result.read()[:-1]
    print(f'all ip {ip}')
    
    ip = ip.split('\n')[int(index)]
    print(f'select ip {ip}')

    port = 8080
    server = HTTPServer((ip, port), HTTPHandler)
    print("Starting server, listening http://%s:%s use <Ctrl-C> to stop" % (ip, port))
    server.serve_forever()
