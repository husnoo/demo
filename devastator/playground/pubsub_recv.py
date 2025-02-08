import pynng
import msgpack

class Sub:
    def __init__(self, address, topic):
        self.topic = topic
        self.topic_enc = topic.encode('ascii')
        self.sub = pynng.Sub0(recv_timeout=10)
        self.sub.dial(address)
        self.sub.subscribe(topic.encode('ascii'))
        print(f"Subscribed to {topic}")

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
        


def subscriber():
    sub = Sub("tcp://127.0.0.1:12345", '/motor_left')
    while True:
        data = sub.recv()
        if data is not None:
            print(f"Received on {sub.topic}: {data}")

if __name__ == "__main__":
    subscriber()
