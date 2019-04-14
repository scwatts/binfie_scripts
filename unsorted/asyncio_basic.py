#!/usr/bin/env python3
'''Written as an example for others'''
import asyncio
import subprocess


def main():
    # Synchronous job execution
    print('Running jobs synchronously...')
    run_task_sync(1, 10)
    run_task_sync(2, 5)


    # Asynchronous job execution
    print('\nRunning jobs asynchronously...')
    # Create a single Future for all coroutines
    async_futures = asyncio.gather(run_task_async(1, 10), run_task_async(2, 5))
    # Create an event loop
    loop = asyncio.get_event_loop()
    # Place the Future we created above on the event loop
    # Remain in the event loop until all coroutines are done
    loop.run_until_complete(async_futures)
    # Once all coroutines in the Future are done, close the event loop
    loop.close()


def run_task_sync(task_number, time):
    # Execute a command synchronously
    print('Task number %s is running' % task_number)
    command = 'sleep %s' % time
    print('Task number %s command \'%s\' has been executed' % (task_number, command))
    print('Task number %s is waiting for command to finish' % task_number)
    process = subprocess.run(command, shell=True)
    # Once the command has run print message
    print('Task number %s is done' % task_number)


async def run_task_async(task_number, time):
    # Execute a command asynchronously (i.e. don't block until it has completed)
    print('Task number %s is running' % task_number)
    command = 'sleep %s' % time
    print('Task number %s command \'%s\' has been executed' % (task_number, command))
    process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    # Within this coroutine, wait until the command has completed
    # Other coroutines can run during this time
    print('Task number %s is waiting for command to finish' % task_number)
    await process.wait()
    # Once the command has run, complete execution of this coroutine
    print('Task number %s is done' % task_number)


if __name__ == '__main__':
    main()
