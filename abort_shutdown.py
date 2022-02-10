import os

def abort_shutdown():
    os.system("shutdown /a")


if __name__ == '__main__':
    abort_shutdown()
