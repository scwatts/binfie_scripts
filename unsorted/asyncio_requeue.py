#!/usr/bin/env python3
'''Written as an example for others'''
import asyncio
import subprocess


class Task():

    running_tasks = 0

    def __init__(self, task_number, time):
        self.task_number = task_number
        self.time = time
        self.max_attempts = 3
        self.attempts = 0

    async def run(self):
        # Wait until there are free job slots
        while Task.running_tasks >= 10:
            await asyncio.sleep(10)

        # Consume a job slot when this job is executed
        Task.running_tasks += 1

        while self.attempts < self.max_attempts:
            print('Task number %s is running' % self.task_number)
            command = 'asleep %s' % self.time
            # Execute a command asynchronously (i.e. don't block until it has completed)
            print('Task number %s command \'%s\' has been executed' % (self.task_number, command))
            process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            # Within this coroutine, wait until the command has completed
            # Other coroutines can run during this time
            print('Task number %s is waiting for command to finish' % self.task_number)
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                print('Task number %s is done' % self.task_number)
                break
            else:
                print('Task number %s failed ' % self.task_number)
                self.attempts += 1
        # Release job count and return
        Task.running_tasks -= 1


def main():
    # Get tasks to run and create Future, eventloop
    tasks = [Task(i, 5) for i in range(1, 2)]
    async_futures = asyncio.gather(*[task.run() for task in tasks])
    loop = asyncio.get_event_loop()

    # Place the Future we created above on the event loop
    # Remain in the event loop until all coroutines are done
    loop.run_until_complete(async_futures)

    # Once all coroutines in the Future are done, close the event loop
    loop.close()


if __name__ == '__main__':
    main()
