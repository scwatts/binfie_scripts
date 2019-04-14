#!/usr/bin/env python3
'''Occasionally you'll want to debug code downstream of a very slow process. This can be a
considerable issue as the your loop to debug and assess becomes prohibitively long. One method to
mitigate the problem is to decouple the slow process from the code to debug. Below is an example in
which a large data is loaded and then in an infinite loop external, code is continuously loaded for
debugging.'''
import os


def main():
  # Load and process large data set
  data = load_data()
  debug = True
  while debug:
      # Child fork executes code to debug while parent waits
      pid = os.fork()
      if 0 == pid:
          import code_to_debug
          code_to_debug.run(data)
          os._exit(0)
      else:
          os.waitpid(pid, 0)
          debug = prompt_try_again()


if __name__ == '__main__':
  main()
