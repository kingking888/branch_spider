from threading import Thread
from Detailspider import QanDaShi

N = 20


def one_thread():
    spider = QanDaShi()
    spider.run()


def main():
    thread_list = [Thread(target=one_thread, ) for _ in range(N)]
    for thread in thread_list:
        thread.start()


if __name__ == '__main__':
    main()
