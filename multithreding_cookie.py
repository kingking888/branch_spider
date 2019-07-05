from threading import Thread
from ppet_get_cookie import Cookei

N = 10


def one_thread():
    spider = Cookei()
    spider.run()


def main():
    thread_list = [Thread(target=one_thread, ) for _ in range(N)]
    for thread in thread_list:
        thread.start()


if __name__ == '__main__':
    main()
