#!/usr/bin/env python3

import logging
import logging.handlers
import multiprocessing as mp
import time
import os
from dotenv import load_dotenv
import json
import log
from config import settings 
import module

STOP = settings.stop 

load_dotenv()

def worker_process(worker_id: int, log_queue: mp.Queue) -> None:
    """
    Example worker process.
    All logs go to the multiprocessing.Queue.
    """
    logger = log.configure_queue_logger(log_queue)

    logger.info("Worker %s started", worker_id)

    for i in range(3):
        logger.debug("Worker %s iteration %s", worker_id, i)
        time.sleep(0.2)

    try:
        if worker_id == 2:
            raise ValueError("Example exception from worker 2")
    except Exception:
        logger.exception("Worker %s hit an exception", worker_id)

    logger.info("Worker %s finished", worker_id)


def main() -> None:
    log_queue = mp.Queue()

    listener = mp.Process(
        target=log.log_listener_process,
        args=(log_queue,),
        name="LogListener",
    )
    listener.start()

    workers = [
        mp.Process(
            target=worker_process,
            args=(i, log_queue),
            name=f"Worker-{i}",
        )
        for i in range(1, 4)
    ]

    for p in workers:
        p.start()

    for p in workers:
        p.join()
        
    module.func(log_queue)

    # Tell the listener to stop after all workers are done
    log_queue.put(STOP)
    listener.join()



if __name__ == "__main__":
    mp.set_start_method("spawn", force=True)
    main()
