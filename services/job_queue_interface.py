from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, Future
import threading


class BaseQueueProvider(ABC):
    @abstractmethod
    def submit(self, fn, *args, **kwargs):
        pass

    @abstractmethod
    def shutdown(self, wait=True):
        pass

    @abstractmethod
    def get_active_count(self):
        pass

    @abstractmethod
    def get_queue_size(self):
        pass


class ThreadPoolQueueProvider(BaseQueueProvider):
    def __init__(self, max_workers=4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = threading.Lock()
        self._futures = {}
        self._counter = 0

    def submit(self, fn, *args, **kwargs):
        future = self.executor.submit(fn, *args, **kwargs)
        with self._lock:
            self._counter += 1
            fid = self._counter
            self._futures[fid] = future
            future._ss_fid = fid
        return future

    def shutdown(self, wait=True):
        self.executor.shutdown(wait=wait)

    def get_active_count(self):
        count = 0
        with self._lock:
            for fid, f in list(self._futures.items()):
                if not f.done():
                    count += 1
                else:
                    del self._futures[fid]
        return count

    def get_queue_size(self):
        return self.executor._work_queue.qsize() if hasattr(self.executor, '_work_queue') else 0


class CeleryQueueProvider(BaseQueueProvider):
    def __init__(self):
        raise NotImplementedError('Celery integration not yet implemented')

    def submit(self, fn, *args, **kwargs):
        raise NotImplementedError('Celery integration not yet implemented')

    def shutdown(self, wait=True):
        pass

    def get_active_count(self):
        return 0

    def get_queue_size(self):
        return 0


class RQQueueProvider(BaseQueueProvider):
    def __init__(self):
        raise NotImplementedError('RQ integration not yet implemented')

    def submit(self, fn, *args, **kwargs):
        raise NotImplementedError('RQ integration not yet implemented')

    def shutdown(self, wait=True):
        pass

    def get_active_count(self):
        return 0

    def get_queue_size(self):
        return 0
