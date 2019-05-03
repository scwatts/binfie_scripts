from . import arguments


import _skeleton


def entry():
    args = arguments.get_args()
    result = _skeleton.quake_invsqrt(args.number)
    print(result)


if __name__ == '__main__':
    entry()
