from threading import Thread
from queue import Queue
from time import sleep

class StoppableWorker(Thread):
    def __init__(self, func: callable, in_queue: Queue, out_queue: Queue):
        super().__init__()
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        for item in self.in_queue:
            result = self.func(item)
            self.out_queue.put(result)
            self.in_queue.task_done()

class ClosableQueue(Queue):
    SENTINEL = object()

    def close(self):
        self.put(self.SENTINEL)
    
    def __iter__(self):
        while True:
            item = self.get()
            if item is self.SENTINEL:
                self.task_done()
                return
            yield item

def consume(queue: Queue):
    print("consume getting")
    print('consume received item: ', queue.get())
    print("consume done")

def produce(queue: Queue):
    print('produce putting')
    queue.put('item 1')
    print('produce done')

def download(work_item: object):
    print('downloading work item: ', work_item)
    sleep(0.1)
    print('download done')
    return f'downloaded {work_item}'

def transform(work_item: object):
    print('transforming work item: ', work_item)
    sleep(0.3)
    print('transform done')
    return f'transformed {work_item}'

def closeable_queue_test():
    download_queue = ClosableQueue()
    transform_queue = ClosableQueue()
    done_queue = ClosableQueue()
    workers = [
        StoppableWorker(download, download_queue, transform_queue),
        StoppableWorker(transform, transform_queue, done_queue),
    ]

    for worker in workers:
        worker.start()

    for i in range(5):
        download_queue.put(f'item {i}')

    download_queue.close()
    download_queue.join()
    transform_queue.close()
    transform_queue.join()

    print(f'Received {done_queue.qsize()} items in the done queue')

    for worker in workers:
        worker.join()

def simple_queue_test():
    my_queue = Queue(1)
    ct = Thread(target=consume, args=[my_queue])
    pt = Thread(target=produce, args=[my_queue])
    ct.start()
    sleep(0.5)
    pt.start()



if __name__ == "__main__":
    simple_queue_test()