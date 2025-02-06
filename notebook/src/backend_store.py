import os
import json
import hashlib
import base64
import socket
#print(socket.gethostname())

# Set time to zero inside gzip so that rewrite of the same data yields identical gzip data
class FakeTime:
    def time(self):
        return 0
import gzip
gzip.time = FakeTime()


if socket.gethostname()=='heisenbug':
    DOCUMENTS_DIR = '/home/nawal/data/shared_large_files/documents'
    NOTEBOOKS_DIR = '/home/nawal/data/shared_large_files/notebooks/notebooks-data'
    OUTPUT_PDF_DIR = '/home/nawal/data/shared_large_files/notebooks/notebooks-pdf'
elif socket.gethostname()=='localhost':
    DOCUMENTS_DIR = '/storage/sdcard0/Nawal-internal/syncthing/documents'
    NOTEBOOKS_DIR = '/storage/sdcard0/Nawal-internal/syncthing/notebooks/notebooks-data/'
else:
    raise Hell()


#if socket.gethostname()=='localhost':
#    file_path = '/storage/sdcard0/Nawal-internal/syncthing/notebooks/stuff/page1.json.gz'
#    with gzip.open(file_path, 'r') as f:
#        page_data = f.read().decode('utf-8')
#    print(page_data)

    
def load_notebook(notebook_name, page_number):
    file_path = os.path.join(NOTEBOOKS_DIR, notebook_name, 'page{}.json.gz'.format(page_number))
    if os.path.exists(file_path):
        with gzip.open(file_path, 'r') as f:
            page_data = f.read().decode('utf-8')
            #print(type(page_data), len(page_data), page_data)
    else:
        page_data = '''{"objects": []}'''
    return page_data

def write_notebook(notebook_name, page_number, page_data):
    dir_path = os.path.join(NOTEBOOKS_DIR, notebook_name)
    file_path = os.path.join(dir_path, 'page{}.json.gz'.format(page_number))
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    with gzip.open(file_path, 'wb') as f:
        f.write(json.dumps(page_data).encode('utf-8'))
    return

def get_num_pages(notebook_name):
    dir_path = os.path.join(NOTEBOOKS_DIR, notebook_name)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    num_pages = len(os.listdir(dir_path))
    return num_pages

def put_image(img_request):
    #print('received:' + data.decode('utf-8'))
    req = json.loads(img_request.decode('utf-8'))
    notebook_name = req['notebook']
    data = bytes(req['data'], 'ascii')
    readable_hash = hashlib.sha256(data).hexdigest()
    pyfname = os.path.join(NOTEBOOKS_DIR, notebook_name, 'snaps', readable_hash+'.png')
    dirname = os.path.dirname(pyfname)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    with open(pyfname, "wb") as fh:
        fh.write(base64.decodebytes(data))
    jsfname = '/snaps/' + notebook_name + '/' + readable_hash+'.png'
    return jsfname

def get_snap(notebook_name, snap_name):
    pyfname = os.path.join(NOTEBOOKS_DIR, notebook_name, 'snaps', snap_name)
    with open(pyfname, "rb") as fh:
        return fh.read()

def get_notebooks():
    notebooks = list(sorted(os.listdir(NOTEBOOKS_DIR)))
    return [nb for nb in notebooks if not nb.startswith('.')]
    








