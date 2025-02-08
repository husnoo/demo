from src.pubsub import Pub, Sub
from src.pubsub import decode_numpy
from src import config


def main():
    pub_target = Pub(config.TARGET_ADDR)    
    while True:
        text = input("What target? ")
        if text.lower() == "exit":
            break
        pub_target.send('/target', text)
        print("OK")

if __name__ == '__main__':
    main()

