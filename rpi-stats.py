import os
import time
import socket
import psutil
import threading
import datetime

from lib.waveshare_epd import epd2in13_V2
from PIL import Image, ImageDraw, ImageFont

# Global definitions
display = epd2in13_V2.EPD()
pic_dir = 'pic_dir'
w = display.width
h = display.height

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def get_machine_storage():
    result=os.statvfs('/')
    block_size=result.f_frsize
    total_blocks=result.f_blocks
    free_blocks=result.f_bfree
    # giga=1024*1024*1024
    giga=1000*1000*1000
    total_size=total_blocks*block_size/giga
    free_size=free_blocks*block_size/giga
    total = str("%s" % round(total_size, 2))
    free = str("%s" % round(free_size, 2))
    return "Disk: "+ free + "/" + total


def clean_screen():
    try:
        # Display init, clear
        display.init(display.FULL_UPDATE)
        display.Clear(0xFF)

    except IOError as e:
        print(e)


def update_dynamic_screen():
      
    print("Updating stats")
    try:
        threading.Timer(5, update_dynamic_screen).start()
        display.init(display.PART_UPDATE)

        w = display.width
        h = display.height

        image = Image.new('1', (display.height, display.width), 255)  # 255: clear the frame    
        draw = ImageDraw.Draw(image)

        # Top line
        draw.line([(0,15),(h,15)], fill = 0,width = 2)

        # Bottom line
        draw.line([(0,w-2),(h,w-2)], fill = 0,width = 2)

        # Print hostname
        draw.text((0, 0), socket.gethostname(), fill = 0)

        # Print IP address
        ip = str(get_ip()).replace("'", "")
        text_font = ImageFont.truetype("/usr/share/fonts/truetype/noto/DejaVuSans-Bold.ttf", 9)
        m_w,m_h = text_font.getsize(ip)
        draw.text(((h-m_w), 0), ip, font=text_font, fill=0)

        draw.text((0, 20), "Stats:", fill = 0)

        # Pring CPU Usage
        cpu_usage = "CPU: " + str(psutil.cpu_percent()) + "%"
        draw.text((0, 30), cpu_usage, fill = 0)

        # Print Memory usage
        mem_usage = "Mem: "+ str(round((psutil.virtual_memory().available * 100 / psutil.virtual_memory().total), 2)) + "%"
        draw.text((0, 40), mem_usage, fill = 0)

        # Print Disk Usage
        draw.text((0, 50), get_machine_storage(), fill = 0)
        
        # Print system uptime
        #datetime.timedelta(seconds=
        #uptime = "UP: " + str(datetime.timedelta(seconds=(time.time() - psutil.boot_time())))
        uptime = "UP: " + time.strftime("%H:%M:%S", time.gmtime(time.time() - psutil.boot_time()))
        draw.text((0, 60), uptime, fill = 0)


        display.displayPartial(display.getbuffer(image))

            

    except IOError as e:
        print(e)
        

def main():
    print("Running rpi-stats.py")
    clean_screen()
    update_dynamic_screen()


if __name__ == "__main__":
    main()
