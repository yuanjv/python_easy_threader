import threading

import concurrent.futures

import queue

#import time



class Threader:

    def __init__(

        self,

        inp_fn,

        works:list,

        max_workers:int=5

    )->None:

        self.queue=queue.Queue()

        self.stop_event=threading.Event()

        self.works_len=len(works)

        self.thread=threading.Thread(

            target=Threader.worker_fn,

            args=(

                Threader.work_fn,

                inp_fn,

                self.queue,

                works,

                max_workers,

                self.stop_event

            )

        )

        self.thread.daemon=True

        self.thread.start()

    

    @staticmethod

    def work_fn(inp_fn,queue,work)->None:

        queue.put(inp_fn(work))

    @staticmethod

    def worker_fn(work_fn,inp_fn,queue,works,max_workers,stop_event)->None:

        with concurrent.futures.ThreadPoolExecutor(

            max_workers=max_workers

        )as executer:

            futures=[]

            for work in works:

                if stop_event.is_set():

                    break

                futures.append(

                    executer.submit(

                        work_fn,

                        inp_fn,

                        queue,

                        work

                    )

                )

            for _ in concurrent.futures.as_completed(futures):

                if stop_event.is_set():

                    break

            if stop_event.is_set():

                executer.shutdown(

                    cancel_futures=True,

                    wait=True

                )

    def get(self):

        if self.works_len!=0:

            self.works_len-=1

            return self.queue.get()

        raise queue.Empty

    def stop(self)->None:

        self.stop_event.set()

    @property

    def is_done(self)->bool:

        return self.works_len==0

    @property

    def is_alive(self)->bool:

        return self.thread.is_alive() 
