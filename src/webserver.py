#!/usr/bin/env micropython

# Early 2021
# Author  metachris some parts by overflo
# Part of frischluft.works
# Filename: webserver.py
# Purpose: Serves files via HTTP
# Known issues: Throws some Exception on 4MB SPIRAM version of WROVER, but works without SPIRAM support
# License Details found @ /LICENSE file in this repository





import gc
import uos
import json
import machine
import ubinascii
import random
from lib import tinyweb, databuffer
from config import update_config_file, CONFIG_FILENAME, IS_CONFIGURED_BY_USER, ADMIN_PASSWORD, THRESHOLD_WARNING_PPM, THRESHOLD_ALERT_PPM, DEVICE_NAME

try:
    unameinfo = list(uos.uname())
except:
    unameinfo = None

# Create webserver instance
app = tinyweb.webserver()

async def require_basicauth(request, response):
    """
    Make sure basic auth is used when needed.
    """
    # print('require_basicauth', request.method, request.path, request.query_string, request.headers)

    # Auth is only required after user configuration
    if not IS_CONFIGURED_BY_USER:
      return

    # Auth is only required if admin password is set
    if not ADMIN_PASSWORD:
      return

    print('basicauth', ADMIN_PASSWORD)

    if not b"Authorization" in request.headers:
        response.add_header('WWW-Authenticate', 'Basic realm="frischluft"')
        response.code = 401
        await response.html('<html><body><h1>Admin interface needs a password</h1></html>\n')
        raise tinyweb.HTTPException(401)

    auth_header = request.headers[b"Authorization"].decode()
    if not auth_header.startswith('Basic '):
        response.add_header('WWW-Authenticate', 'Basic realm="frischluft"')
        response.code = 401
        await response.html('<html><body><h1>Invalid auth header</h1></html>\n')
        raise tinyweb.HTTPException(401)

    credentials = ubinascii.a2b_base64(auth_header[6:]).decode()
    user, pwd = credentials.split(':')
    if user != "admin" or pwd != ADMIN_PASSWORD:
        response.code = 401
        response.add_header('WWW-Authenticate', 'Basic realm="frischluft"')
        await response.html('<html><body><h1>Invalid username / password</h1></html>\n')
        raise tinyweb.HTTPException(401)


@app.route('/')
@app.route('/index.html')
async def index(request, response):
    print("web request: index")
    await response.send_file('webfiles-static/index.html')


# @app.catchall()
# async def error_handler(request, response):
#     await response.send_file('webfiles-static/error.html')


@app.route('/favicon.ico')
async def index(request, response):
    await response.send_file('webfiles-static/favicon.ico')


@app.route('/webfiles-static/<fn>')
async def static_files_handler(req, resp, fn):
    await resp.send_file('webfiles-static/{}'.format(fn))


@app.route('/admin', methods=["GET"], save_headers=["Authorization"])
async def admin_handler(request, response):
    # print('headers', request.headers)
    await require_basicauth(request, response)
    f = "</title>"

    response.add_header('Access-Control-Allow-Credentials', 'true')
    await response.send_file('webfiles-static/internal/admin.html')


@app.route('/status')
async def get_status(request, response):
    print("web request: status")

    # For development, when running this file from console, add a dummy datapoint on each request
    if __name__ == '__main__':
        databuffer.add_datapoint('ppm', 500 + random.getrandbits(30) % 1500, force=True)
        databuffer.add_datapoint('humidity', 500 + random.getrandbits(30) % 100, force=True)
        databuffer.add_datapoint('temp', 500 + random.getrandbits(30) % 50, force=True)

    # Build the response body
    body = {
        "dataBuffers": databuffer.buffers,
        "dataInterval": databuffer.SECONDS_BETWEEN_ENTRIES,
        "isConfiguredByUser": IS_CONFIGURED_BY_USER,
        "thresholdWarningPpm": THRESHOLD_WARNING_PPM,
        "thresholdAlertPpm": THRESHOLD_ALERT_PPM,
        "sysInfo": {
            "deviceName": DEVICE_NAME,
            "memFree": gc.mem_free(),
            "uname": unameinfo,
            "fsInfo": uos.statvfs('/')
        }
    }

    await response.json(body)


@app.route('/get-config', save_headers=["Authorization"])
async def get_config_handler(request, response):
    await require_basicauth(request, response)

    config_content = open(CONFIG_FILENAME).read()
    response.add_header('Content-Type', 'application/json')
    await response._send_headers()
    await response.send(config_content)


@app.route('/save-config', methods=["GET", "POST"], save_headers=["Content-Length", "Content-Type", "Authorization"], max_body_size=2000)
async def save_config_handler(request, response):
    await require_basicauth(request, response)

    data = await request.read_parse_form_data()  # returns json already
    # print('headers', request.headers)
    # print('data', data)

    # If data is not a dict then return HTTP error 400
    if not isinstance(data, dict):
        raise tinyweb.HTTPException(400)

    # Now update local config and return OK
    update_config_file(data)
    response.add_header('Content-Type', 'application/json')
    await response._send_headers()
    await response.send(json.dumps({"success": True}))


@app.route('/reset', save_headers=["Authorization"])
async def reset_system(request, response):
    await require_basicauth(request, response)

    print("resetting through /reset...")
    try:
        from driver import display
        d = display.Display()
        d.show_restart()
    except:
        pass
    machine.reset()


# for local development
def run():
    host = '0.0.0.0'
    port = 8081
    print("Listening on %s:%s" % (host, port))
    app.run(host=host, port=port)


if __name__ == '__main__':
    for i in range(30):
        databuffer.add_datapoint('ppm', 500 + random.getrandbits(30) % 1500, force=True)

    run()
