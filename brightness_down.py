import os

def set_brightness(percentage):
    os.system("powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1," + str(percentage) + ")")


def brightness_up():
    set_brightness(100)


def brightness_down():
    set_brightness(0)


if __name__ == '__main__':
    brightness_up()
    brightness_down()
