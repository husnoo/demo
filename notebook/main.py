#!/usr/bin/env python

# WS server that sends messages at random intervals
# Serve the main page from this app too


#import asyncio
#import datetime
#import random
#import websockets
import bottle
#import threading
import json
import src.backend_store
import os
import pathlib
RUN_DIR = pathlib.Path(__file__).parent.absolute()

'''
async def time(websocket, path):
    while True:
        now = datetime.datetime.utcnow().isoformat() + "Z"
        await websocket.send(now)
        await asyncio.sleep(random.random() * 3)


def thread_function():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    start_server = websockets.serve(time, "0.0.0.0", 5678)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
'''


@bottle.route('/notebook/<notebook>')
def notebook(notebook):
    with open(os.path.join(RUN_DIR,'www/notebook.html'), 'r') as f:
       data = f.read()
    return data

@bottle.route('/reader/<notebook>')
def reader(notebook):
    with open(os.path.join(RUN_DIR, 'www/reader.html'), 'r') as f:
       data = f.read()
    return data


@bottle.route('/get-notebook-data/<notebook_name>/<page_number>')
def get_notebook_data(notebook_name, page_number):
    page_data = src.backend_store.load_notebook(notebook_name, page_number)
    return json.dumps(page_data)


@bottle.post('/set-notebook-data/<notebook_name>/<page_number>')
def set_notebook_data(notebook_name, page_number):
    body = bottle.request.body.read().decode('utf-8')
    page_data = json.loads(body)
    src.backend_store.write_notebook(notebook_name, page_number, page_data)
    return 'ok'


@bottle.post('/put-image')
def put_image():
    body = bottle.request.body.read()
    fname = src.backend_store.put_image(body)
    return fname


@bottle.get('/snaps/<notebook_name>/<snap_name>')
def get_snap(notebook_name, snap_name):
    bottle.response.content_type ='image/png'
    return src.backend_store.get_snap(notebook_name, snap_name)


@bottle.get('/get-notebook-num-pages/<notebook_name>')
def get_num_pages(notebook_name):
    num_pages = src.backend_store.get_num_pages(notebook_name)
    return str(num_pages)

@bottle.route('/<filepath:path>')
def server_static(filepath):
    return bottle.static_file(filepath, root=os.path.join(RUN_DIR,'www'))


@bottle.route('/cordova.js')
def cordova():
    return ''


@bottle.route('/')
def index():
    notebooks = src.backend_store.get_notebooks()
    out = ''
    out += '''
<html>
<head>
<style>
body {
    zoom: 3; 
    -moz-transform: scale(3); 
    -moz-transform-origin: 0 0;
}

.one-notebook {
    margin-top: 10px;
    margin-bottom: 10px;
    background-color: #cfa;
    width: 400px;
    text-align: center;
    padding: 10px;
}



.one-notebook a {
    padding: 5px;
    font-size: 24px;
}
</style>
</head>
<body>
'''
    for notebook in notebooks:
        out += '<div class="one-notebook">'
        out += '{}<br><a href="/notebook/{}">Edit</a> <a href="/reader/{}">View</a>'.format(notebook, notebook, notebook)
        out += '</div>'

    out += '''
</body>
</html>
'''
    return out


def main():
    #x = threading.Thread(target=thread_function)
    #x.start()
    bottle.run(host='0.0.0.0', port=8080, reloader=False)

if __name__=='__main__':
    main()
