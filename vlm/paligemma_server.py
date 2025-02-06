# scp /home/nawal/data/calcifer/data/vae-oid.npz rita:/home/nawal/storage/calcifer/data

import datetime
import os
import socket
import sys
import time

#import bottle
import msgpack
import numpy
import pynng
import transformers
#bottle.BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024

if socket.gethostname()=='rita':
    vae_loc = os.path.join('/home/nawal/storage/calcifer','data', 'vae-oid.npz')
    use_reloader = False # don't use reloader on rita because it uses 2x memory!
    sys.path.append('/home/nawal/storage/calcifer')
else:
    vae_loc = os.path.join('/home/nawal/data/calcifer','data', 'vae-oid.npz')
    use_reloader = True
    sys.path.append('/home/nawal/data/calcifer')

import src.paligemma.paligemma_parse
src.paligemma.paligemma_parse._MODEL_PATH = vae_loc


#model_id = "google/paligemma2-3b-pt-224" # this is from the new versions
model_id = "google/paligemma2-3b-ft-docci-448" # Try this, might be smarter
#model_id = "google/paligemma-3b-mix-224" # (the one from the demo!!)


model = transformers.PaliGemmaForConditionalGeneration.from_pretrained(model_id)
model = model.to("cuda")
processor = transformers.AutoProcessor.from_pretrained(model_id)


#@bottle.route('/paligemma2', method="POST")
#def route_paligemma2():
#    # TODO: lazy load model based on json['model'] and maybe change model if new one comes along
#    time_start = datetime.datetime.now()
#    image = numpy.array(bottle.request.json['image'], dtype=numpy.uint8)
#    prompt = bottle.request.json['prompt']
#    time_decode_request = datetime.datetime.now()    
#    inputs = processor(prompt, image, return_tensors="pt").to("cuda")
#    # https://huggingface.co/google/paligemma-3b-mix-448/discussions/6
#    time_prep_input = datetime.datetime.now()        
#    output = model.generate(**inputs, max_new_tokens=50)
#    time_calc_output = datetime.datetime.now()
#    response = processor.decode(output[0], skip_special_tokens=True)
#    objects = src.paligemma.paligemma_parse.extract_objs(
#        response.split('\n')[1], image.shape[1], image.shape[0], unique_labels=True)
#    for obj in objects:
#        if 'mask' in obj and obj['mask'] is not None:
#            obj['mask'] = obj['mask'].tolist()
#    time_decoded = datetime.datetime.now()
#    print('time1:', time_decode_request-time_start)
#    print('time2:', time_prep_input-time_start)
#    print('time3:', time_calc_output-time_start)
#    print('time4:', time_decoded-time_start)
#    return {"result": response, 'objects': objects}
#
#
#bottle.run(host='0.0.0.0', port=8089, debug=True, reloader=use_reloader)

addr = 'tcp://192.168.0.52:8089'
#addr = 'tcp://192.168.0.10:8089'
with pynng.Pair0(recv_timeout=100, send_timeout=1) as sock:
    print('Listening on ', addr)
    sock.listen(addr)
    while True:
        try:
            #time_start = datetime.datetime.now()
            msg = sock.recv()
            print('got message')
            ret = msgpack.unpackb(msg)
            image_shape = ret['image_shape']            
            image = numpy.frombuffer(ret['image'], dtype=numpy.uint8).reshape(image_shape)
            prompt = ret['prompt']
            max_tokens = ret["max-tokens"]
            #time_decode_request = datetime.datetime.now()    

            #print(image.shape, image.dtype, prompt,  image[240,:,0])
            #print('time_decode_request-time_start:', time_decode_request-time_start)

            inputs = processor(prompt, image, return_tensors="pt").to("cuda")
            # https://huggingface.co/google/paligemma-3b-mix-448/discussions/6
            #time_prep_input = datetime.datetime.now()        
            output = model.generate(**inputs, max_new_tokens=max_tokens)
            #time_calc_output = datetime.datetime.now()
            response = processor.decode(output[0], skip_special_tokens=True)
            objects = src.paligemma.paligemma_parse.extract_objs(
                response.split('\n')[1], image.shape[1], image.shape[0], unique_labels=True)
            for obj in objects:
                if 'mask' in obj and obj['mask'] is not None:
                    print('obj["mask"].shape', obj['mask'].shape)
                    obj['mask'] = numpy.array(obj['mask']>0, dtype=numpy.uint8).tobytes()
            #time_decoded = datetime.datetime.now()
            #print('time1:', time_decode_request-time_start)
            #print('time2:', time_prep_input-time_start)
            #print('time3:', time_calc_output-time_start)
            #print('time4:', time_decoded-time_start)
            result = {"result": response, 'objects': objects}
            sock.send(msgpack.packb(result))
        except pynng.Timeout:
            pass
        time.sleep(0.1)


