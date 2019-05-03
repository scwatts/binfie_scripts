from . import arguments
from . import utils


def entry():
    args = arguments.get_args()
    result = utils.quake_invsqrt(args.number)
    print(result)


if __name__ == '__main__':
    entry()
