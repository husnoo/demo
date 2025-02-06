import glob
import gzip
import json
import pprint
import os

import reportlab.lib.pagesizes
import reportlab.pdfgen.canvas
import backend_store

# https://www.reportlab.com/docs/reportlab-userguide.pdf

def handle_object(notebook_name, canvas, object, xscale, yscale, page_width_px, page_height_px, top=0, left=0):
    if object['type'] == 'path':
        prev = []
        #print(object.keys())
        #print(object['left'], object['top'], object['originX'], object['originY'], object['width'], object['height'], object['pathOffset'])
        # 143.0791791520642 120.42311154165914 center center 281.75 231.29 {'x': 143.0791791520642, 'y': 120.42311154165914}
        # 426.2147878468362 126.62316782351179 center center 281.75 231.29 {'x': 143.0791791520642, 'y': 120.42311154165914}
        for segment in object['path']:
            if segment[0] == 'Q':
                #print(segment)
                x1 = (left + segment[1] + object['left'] - object['pathOffset']['x']) * xscale
                y1 = (page_height_px - (segment[2] + top + object['top'] - object['pathOffset']['y'])) * yscale
                x2 = (left + segment[3] + object['left'] - object['pathOffset']['x']) * xscale
                y2 = (page_height_px - (segment[4] + top + object['top'] - object['pathOffset']['y'])) * yscale
                if prev != []:    
                    canvas.line(prev[0], prev[1], x1, y1)
                canvas.line(x1, y1, x2, y2)
                prev = [x2, y2]
    elif object['type'] == 'textbox':
        #print(object.keys())
        canvas.setFont('Helvetica', object['fontSize']/4.0)
        x = object['left'] * xscale
        y = (page_height_px - object['top'] - object['height']/3.0) * yscale
        textobject = canvas.beginText(x, y)
        #textobject.setFont(psfontname, size, leading = None)
        textobject.textLines(object['text'])
        canvas.drawText(textobject)
        # Text wrap: https://stackoverflow.com/a/32830704/611660
        #print(list(object['text']))
        #'originX': 'left', 'originY': 'top',
        # 'left': 1206.07, 'top': 530.65,
        # 'width': 93.32, 'height': 97.63,
        # 'text': 'Hello world', 'fontSize': 40, 'lineHeight': 1.16            
    elif object['type'] == 'image':
        #print(object)
        width = object['width'] * object['scaleX'] * xscale
        height = object['height'] * object['scaleY'] * yscale
        x = object['left'] * xscale
        y = (page_height_px - object['top']) * yscale - height        
        notebook, img_name = object['src'].replace('http://127.0.0.1:8080/snaps/', '').split('/')
        img_path = os.path.join(backend_store.NOTEBOOKS_DIR, notebook_name, 'snaps', img_name)
        canvas.drawImage(img_path, x, y, width=width,height=height)
    elif object['type'] == 'group':
        #print('------')
        #print(json.dumps(object))
        #print('------')
        #exit()
        for obj2 in object['objects']:
            handle_object(notebook_name, canvas, obj2, xscale, yscale, page_width_px, page_height_px, top+object['top'], left+object['left'])
    else:
        print('NOT IMPLEMENTED:', object['type'])



def generate_pdf(input_notebook):
    ifname_tmpl = '{}/{}/page{}.json.gz'
    num_pages = len(glob.glob(ifname_tmpl.format(backend_store.NOTEBOOKS_DIR, input_notebook, '*')))

    page_width_mm, page_height_mm = reportlab.lib.pagesizes.A4
    page_width_px = 2480
    page_height_px = 3507
    #print(page_width_mm, page_height_mm, page_width_px, page_height_px)
    xscale = page_width_mm / page_width_px
    yscale = page_height_mm / page_height_px

    canvas = reportlab.pdfgen.canvas.Canvas(os.path.join(backend_store.OUTPUT_PDF_DIR, input_notebook + '.pdf'), pagesize=reportlab.lib.pagesizes.A4, pageCompression=1)
    canvas.setLineWidth(.3)
    canvas.setFont('Helvetica', 12)
    canvas.setDash(array=[], phase=0)

    for pageno in range(1, num_pages + 1):
        with gzip.open(ifname_tmpl.format(backend_store.NOTEBOOKS_DIR, input_notebook, pageno), 'r') as f:
            page_data = f.read().decode('utf-8')
        json_data = json.loads(page_data)
        for object in json_data['objects']:
            handle_object(input_notebook, canvas, object, xscale, yscale, page_width_px, page_height_px)
        canvas.showPage()
    canvas.save()

import sys
if len(sys.argv) == 1:
    notebooks = backend_store.get_notebooks()
    for notebook in notebooks:
        print('Generating for:', notebook)
        generate_pdf(notebook)
        
else:
    input_notebook = sys.argv[1] #'samples'
    print('Generating for:', input_notebook)
    generate_pdf(input_notebook)




