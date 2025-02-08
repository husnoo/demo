import pynng
import msgpack
import time

class Pub:
    def __init__(self, address):
        self.pub = pynng.Pub0()
        self.pub.listen(address)

    def send(self, topic, value):
        msg = topic.encode('ascii') + msgpack.packb(value)
        print(type(msg))
        self.pub.send(msg)
        print(f"published to {topic}, value={value}")


def publisher():
    pub = Pub("tcp://127.0.0.1:12345")
    i = 1
    while True:
        value = {"speed": 5, 'i': i}
        pub.send('/motor_left', value)
        time.sleep(1)
        i = i + 1

if __name__ == "__main__":
    publisher()
