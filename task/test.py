from .celery import capp, logger
import time

@capp.task(bind=True)
def start_processing(self):
    # Lets simulate a long running task here. By long running we are
    # talking even tasks that take just a minute even. Lets pretend to
    # read a file that takes 1 minute to be read, and it contains just
    # a "Hello World"
    logger.info('Reading a book :|')
    print('Reading a book :|')
    with open('assets/temp.txt', 'r') as file:
        result = file.read()
    time.sleep(3)
    logger.info('Done reading a book :)')
    print('Done reading a book :)')
    return result


@capp.task
def my_celery_task(arg1, arg2):
    # Your task logic here
    return arg1 + arg2
