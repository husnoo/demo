import pynng
import msgpack
import numpy


class Pub:
    def __init__(self, address):
        self.pub = pynng.Pub0()
        self.pub.listen(address)

    def send(self, topic, value):
        msg = topic.encode('ascii') + msgpack.packb(value)
        #print(type(msg))
        self.pub.send(msg)
        #print(f"published to {topic}, value={value}")


class Sub:
    def __init__(self, address, topic):
        self.topic = topic
        self.topic_enc = topic.encode('ascii')
        self.sub = pynng.Sub0(recv_timeout=10)
        self.sub.dial(address)
        self.sub.subscribe(topic.encode('ascii'))
        #print(f"Subscribed to {topic}")

    def recv(self):
        try:
            msg = self.sub.recv()
        except pynng.Timeout as err:
            return None
        topic, packed_data = msg[:len(self.topic_enc)], msg[len(self.topic_enc):]
        if topic.decode('ascii')==self.topic:
            data = msgpack.unpackb(packed_data)
            return data
        else:
            return None


def encode_numpy(value):
    encoded = {
        'value': value.tobytes(),
        "shape": value.shape
    }
    return encoded


def decode_numpy(encoded):
    value = numpy.frombuffer(encoded['value'], dtype=numpy.uint8).reshape(encoded['shape'])
    return value

