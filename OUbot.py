### 540*900 res portrait mode NOX Emulator 
from ppadb.client import Client as AdbClient
adb = AdbClient(host='127.0.0.1', port=5037)
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
import os
import glob
import time
import csv
import logging
import urllib
import re
AVG_RESPONSE_TIME = 1 # Device response time in seconds
logging.basicConfig(filename='testpy.log', level=logging.INFO,format='%(levelname)s: %(message)s   %(asctime)s')

### IMAGES
ICONS={
    'pop_select':Image.open('AutomationImages/pop_select_all.png'),
    'pop_paste':Image.open('AutomationImages/pop_paste.png'),
    'pop_ccp':Image.open('AutomationImages/pop_ccp.png'),
    'pop_ccps':Image.open('AutomationImages/pop_ccps.png'),
    'pop_menu':Image.open('AutomationImages/pop_menu.png'),
    'but_post':Image.open('AutomationImages/but_post.png'),
    'switch_off':Image.open('AutomationImages/pp3_firm_off.png'),
    'switch_on':Image.open('AutomationImages/pp3_firm_on.png'),
    'pp1_but_delete':Image.open('AutomationImages/pp1_but_delete.png'),
    'pp1_but_sp':Image.open('AutomationImages/pp1_select_photo.png'),
    'pp1_camera':Image.open('AutomationImages/pp1_camera.png'),
    'pp1_title_us':Image.open('AutomationImages/pp1_title_unselected.png'),
    'pp1_title_s':Image.open('AutomationImages/pp1_title_selected.png'),
    'pp1_sel_photo':Image.open('AutomationImages/pp1_select_photo.png'),
    'pp2_desc':Image.open('AutomationImages/pp2_desc.png'),
    'pp2_con':Image.open('AutomationImages/ou_pp2_condition.png'),
    'pp2_cat':Image.open('AutomationImages/ou_pp2_category.png'),
}
SIZE={
    'XS':Image.open('AutomationImages/pp4_xs.png'),
    'S':Image.open('AutomationImages/pp4_s.png'),
    'M':Image.open('AutomationImages/pp4_m.png'),
    'L':Image.open('AutomationImages/pp4_l.png'),
}
CONDITION={
    '1':Image.open('AutomationImages/ou_pp2_con_1.png'),
    '2':Image.open('AutomationImages/ou_pp2_con_2.png'),
    '3':Image.open('AutomationImages/ou_pp2_con_3.png'),
    '4':Image.open('AutomationImages/ou_pp2_con_4.png'),
    '5':Image.open('AutomationImages/ou_pp2_con_5.png'),
}
CATEGORY={
    '1':Image.open('AutomationImages/Cat/cs1.png'),
    '2':Image.open('AutomationImages/Cat/cs2.png'),
    '3':Image.open('AutomationImages/Cat/cs3.png'),
    '4':Image.open('AutomationImages/Cat/cs4.png'),
    '5':Image.open('AutomationImages/Cat/cs5.png'),
    '6':Image.open('AutomationImages/Cat/cs6.png'),
    '7':Image.open('AutomationImages/Cat/cs7.png'),
    '8':Image.open('AutomationImages/Cat/cs8.png'),
    '9':Image.open('AutomationImages/Cat/cs9.png'),
    '10':Image.open('AutomationImages/Cat/cs10.png'),
    '11':Image.open('AutomationImages/Cat/cs11.png'),
    '12':Image.open('AutomationImages/Cat/cs12.png'),
    '13':Image.open('AutomationImages/Cat/cs13.png'),
    '14':Image.open('AutomationImages/Cat/cs14.png'),
}


### ADB CLIPBOARD FUNCTIONS

def initClip(device):
    device.install('AdbClipboard2.0.3.apk')

def writeToDevice(device, text):
    urlEncodedString = urllib.parse.quote_plus(text)
    adbProcess = device.shell('am broadcast -n ch.pete.adbclipboard/.WriteReceiver -e text '+urlEncodedString)
    print("write device response from device",adbProcess)
    return adbProcess

def readFromDevice(device):
    adbProcess = device.shell('am broadcast -n ch.pete.adbclipboard/.ReadReceiver')
    print("read device response from device",adbProcess)
    return adbProcess


### IMAGE LOOKUP FUNCTIONS
def imsearch(screen,search,precision=0.8):
    img_rgb = np.array(screen)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.cvtColor(np.array(search), cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    if max_val < precision:
        return False
    return [max_loc,min_loc,max_val]

def where_am_i(screen):     # find out which screen user is in
    TemplateImgs={
        'home':Image.open('AutomationImages/nox_home.png'),
        'OU_home':Image.open('AutomationImages/ou_home.png'),
        'OU_pp_1':Image.open('AutomationImages/ou_pp1.png'),
        'OU_pp_2_cat':Image.open('AutomationImages/ou_pp2_cat.png'),
        'OU_pp_2_con':Image.open('AutomationImages/ou_pp2_con.png'),
        'OU_pp_2':Image.open('AutomationImages/ou_pp2.png'),
        'OU_pp_3':Image.open('AutomationImages/ou_pp3.png'),
        'OU_pp_4_loc':Image.open('AutomationImages/ou_pp4_loc.png'),
        'OU_pp_4':Image.open('AutomationImages/ou_pp4.png'),
        'OU_splash':Image.open('AutomationImages/ou_splash.png'),
        'OU_splash2':Image.open('AutomationImages/ou_splash2.png'),
    }
    for key,value in TemplateImgs.items():
        search=imsearch(screen,value)
        if(search):
            logging.info("where_am_i: "+key+str(search))
            return key,search
    logging.info("where_am_i: Lost")
    return "Lost",((-1,-1),(-1,-1))



#### ADB FUNCTIONS
def get_devices():
    logging.info("Finding ADB Devices")
    devices = adb.devices()
    if len(devices) == 0:
        print('no device attached')
        quit()
    a=[]
    for device in devices:
        serial=device.get_serial_no()
        prop=device.get_properties()
        manufacturer=prop['ro.product.manufacturer']
        model=prop['ro.product.model']
        # print(manufacturer,model)
        a.append([device,serial,manufacturer,model])
        logging.info(manufacturer+" "+model+" "+serial)
    return a

def get_screenshot(device,imagename=False):
    image=device.screencap()
    if imagename:
        with open(imagename+".png", 'wb') as f:
            f.write(image)
    image = Image.open(BytesIO(image))
    return image    #Returns <PIL.PngImagePlugin.PngImageFile image mode=RGBA size=540x960 at 0x8E7AAACD88>

def get_window_dump(device):    # saves dump to folder needs uiautomator
    device.shell('uiautomator dump')
    devices[0].pull('/storage/emulated/0/window_dump.xml','dump.xml')

def send_over_adb(device,hostpath,devpath="/storage/emulated/0/OUBOT/"):      # Recursively send folder and files over adb
    if os.path.isfile(hostpath):
        devpath = os.path.join(devpath,hostpath).replace('\\','/') # optimization for windows
        device.push(hostpath, devpath)
    elif os.path.isdir(hostpath):
        for i in glob.glob(hostpath+'\*'):
            print(i)
            send_over_adb(device,i,devpath)
    device.shell('am broadcast -a android.intent.action.MEDIA_MOUNTED -d file:///mnt/sdcard')
    device.shell('am force-stop com.android.gallery3d') #force create thumbnails

#SIMPLE ANDROID ACTIONS USING SHELL

def go_home(device):
    device.shell('input keyevent 3')

def go_back(device,repeat=1):
    for i in range(i):
        device.shell('input keyevent 4')

def kill_app(device,package_name='com.offerup'):
    device.shell('am force-stop '+package_name)

def kill_all_apps(device):  #only for 540*960 portrait mode NOX EMULATOR android 7
    dev[0].shell('input keyevent KEYCODE_APP_SWITCH')
    for i in range(3):
        dev[0].shell('input swipe 220 125 260 725 1000')
    dev[0].shell('input tap 481 58')

def restart_app(device,package_name='com.offerup'):
    kill_app(device,package_name)
    go_home(device)
    device.shell('am start -n '+package_name+'/'+package_name+'.MainActivity')
    return True

def paste(device):
    device.shell('input keyevent KEYCODE_PASTE')
    return True

def click(device,x,y,dur=0):
    print("click",x,y,dur)
    if(x==-1 or y==-1):
        return
    if(dur==0):
        device.shell('input tap '+str(x)+' '+str(y))
    else:
        device.shell('input swipe '+str(x)+' '+str(y)+' '+str(x)+' '+str(y)+' '+str(dur))

def tap_hold(device,x,y):
    click(device,x,y)
    click(device,x,y,500)

def swipe(device,x1,y1,x2,y2,dur=500):
    device.shell('input swipe '+str(x1)+' '+str(y1)+' '+str(x2)+' '+str(y2)+' '+str(dur))

def wait_for_it(dur=AVG_RESPONSE_TIME,message="sleeping"):
    print(message,dur,end="")
    time.sleep(dur*AVG_RESPONSE_TIME)
    print("  Done")
 
## SPECIFIC FUNCTIONS
def pp1_delete_all_images(device):
    a=True
    call=0
    while(a):
        if call==10:
            return False
        scr=get_screenshot(device)
        wami=where_am_i(scr)
        if(wami[0]!='OU_pp_1'):
            if(wami[0]=='OU_pp_2'):
                click(device,29,59)
            call+=1
            wait_for_it()
            continue
        logging.info(str(wami)+" DELETE ALL IMAGES")
        a=imsearch(scr,ICONS['pp1_but_delete'])
        if a:
            x=a[0][0]#+a[1][0]
            y=a[0][1]#+a[1][1]
            print(a,"del",x,y)
            click(dev[0],x,y)
            wait_for_it(AVG_RESPONSE_TIME)
    return True

def select_all_delete(device,x=None,y=None):
    if(x):
        tap_hold(device,x,y)
        wait_for_it(AVG_RESPONSE_TIME)
    scr=get_screenshot(device)
    b=imsearch(scr,ICONS['pop_select'])
    if b:
        print(b,"sel")
        click(device,b[0][0],b[0][1])
        device.shell("input keyevent KEYCODE_DEL")
        return True
    else:
        b=imsearch(scr,ICONS['pop_menu'])
        if b:
            print(b,"menu")
            click(device,b[0][0],b[0][1])
            scr=get_screenshot(device)
            b=imsearch(scr,ICONS['pop_select'])
            if b:
                print(b,"sel")
                click(device,b[0][0],b[0][1])
                device.shell("input keyevent KEYCODE_DEL")
                return True
    return False

def ou_init(device,imfolder="Input/"):   ###INIT OFFERUP APP AND OPEN POST PAGE 1
    device.shell("rm -r /storage/emulated/0/OUBOT/")
    send_over_adb(device,imfolder)
    call=0
    restart_app(device)
    wait_for_it(3)
    while True:
        if(call==10):
            break
        scr=get_screenshot(device)
        wami=where_am_i(scr)
        print(wami[0])
        if(wami[0]=='OU_pp_1'):
            return True
        if(wami[0]=='OU_home'):
            b=imsearch(scr,ICONS['but_post'])
            if b:
                print(b,"post_btn clicking")
                click(device,b[0][0],b[0][1])
            else:
                click(device,270,930)
            wait_for_it(2)
        elif(wami[0]=='OU_splash' or wami[0]=='OU_splash2' or wami[0]=='home' or wami[0]=='L'):
            wait_for_it(3)
            call+=1
    return False


def pp1_clean(device,text="default"):    ##CLEAN OUT POST PAGE 1 if previous customizations exists and add text to title
    print("PP1 Cleaner")
    writeToDevice(device,text)
    scr=get_screenshot(device)
    wami=where_am_i(scr)
    if(wami[0]=='OU_home'):
        click(device,270,930)
        wait_for_it(5)
    if not pp1_delete_all_images(dev[0]):
        return False
    scr=get_screenshot(device)
    a=imsearch(scr,ICONS['pp1_title_us'])
    if a:
        # print(a,"PP1_title US")
        select_all_delete(dev[0],450,a[0][1]+50)
        paste(device)
        return True


def pp1_add_imgs(device):
    print("PP1 Add Images")
    while True:
        scr=get_screenshot(device)
        a=imsearch(scr,ICONS['pp1_sel_photo'])
        # print(a,"LOOP1")  
        if a:
            click(device,a[0][0],a[0][1])
            click(device,a[0][0],a[0][1],100)
            wait_for_it(3)
            scr=get_screenshot(device)
            a=imsearch(scr,ICONS['pp1_camera'])
            if a:
                break
    click(device,266,184)
    click(device,444,184)
    click(device,88,365)
    click(device,266,365)
    click(device,444,365)
    click(device,88,545)
    click(device,266,545)
    click(device,444,545)
    click(device,272,910,100)
    wait_for_it()
    return True

def pp2_set(device,desc="Demo Description",Condition="1",Category="1,2"):
    print("PP2 Set")
    writeToDevice(device,desc)
    call=0
    while True:     ## SET DESCRIPTION
        if call==10:
            return False
        scr=get_screenshot(device)
        ims=imsearch(scr,ICONS['pp2_desc'])
        if ims:
            select_all_delete(device,ims[0][0]+100,ims[0][1]+100)
            paste(device)
            break
        else:
            call+=1
    call=0
    while True:     ## SET CONDITION
        if call==10:
            return False
        scr=get_screenshot(device)
        ims=imsearch(scr,ICONS['pp2_con'])
        click(device,ims[0][0]+10+call,ims[0][1]+20+2*call)
        wait_for_it(2)
        scr=get_screenshot(device)
        wami=where_am_i(scr)
        if(wami[0]=="OU_pp_2_con"):
            ims=imsearch(scr,CONDITION[Condition])
            if ims:
                click(device,ims[0][0]+15,ims[0][1]+30)
                wait_for_it(2)
                scr=get_screenshot(device)
                wami=where_am_i(scr)
                if(wami[0]=='OU_pp_2'):
                    break
            else:
                call+=1
                continue
        else:
            call+=1
            continue
    return True

def pp2_set_cat(device,cat="1,1"):
    c,sc=cat.split(",")
    call=0
    while True:
        if(call==10):
            return False
        scr=get_screenshot(device)
        wami=where_am_i(scr)
        print(wami,call)
        if(wami[0]=='OU_pp_2'):
            ims=imsearch(scr,ICONS['pp2_cat'])
            click(device,ims[0][0]+20+call*2,ims[0][1]+20+call*5)
            wait_for_it(2)
            call+=1
            continue
        elif(wami[0]=='OU_pp_2_cat'):
            swipe(device,350,150,350,780,120)
            swipe(device,350,150,350,780,120)
            break
        else:
            call+=1
    call=0
    CATH=CATEGORY[c]
    CAT0 = Image.open('AutomationImages/Cat/'+c+',1.png')
    CATR=Image.open('AutomationImages/Cat/'+cat+'.png')
    while True:
        scr=get_screenshot(device)
        wami=where_am_i(scr)
        if(wami[0] != 'OU_pp_2_cat'):
            return pp2_set_cat(device,cat)
        if call==10:
            return False
        ims=imsearch(scr,CATH)
        if not ims:
            swipe(device,350,780,350,150,300)
            # swipe(device,350,780,350,150,200)
            wait_for_it()
            call+=1
            continue
        else:
            if(ims[0][1]>500):
                swipe(device,350,ims[0][1],380,150,500)
                wait_for_it()
            scr=get_screenshot(device)
            scs=imsearch(scr,CATR)
            if(scs):
                click(device,scs[0][0],scs[0][1])
                wait_for_it()
                return True
            else:
                scs0 = imsearch(scr,CAT0)
                if not scs0:
                    ims=imsearch(scr,CATEGORY[c])
                    if ims:
                        click(device,ims[0][0],ims[0][1])
                        continue
                else:
                    swipe(device,350,450,380,150,500)
                    call+=1
                    continue

def pp3_set(device,price="100",firm=False):
    print("PP3 Set")
    call=0
    writeToDevice(device,price)
    while True:
        if call==10:
            return False
        scr=get_screenshot(device)
        wami=where_am_i(scr)
        if(wami[0]=="OU_pp_3"):
            select_all_delete(device,275,144)
            paste(device)
            click(device,169,458)
            break
        elif(wami[0]=='OU_pp_1'):
            click(device,272,910,100)
            wait_for_it(3)
        elif(wami[0]=='OU_pp_2'):
            click(device,272,925,100)
            wait_for_it(3)
        else:
            call+=1
    call=0
    while True:
        if(call==10):
            return False
        scr=get_screenshot(device)
        imsoff = imsearch(scr,ICONS['switch_off'])
        imson = imsearch(scr,ICONS['switch_on'])
        # print(imsoff,imson)
        if firm:
            if imson:
                return True
            elif imsoff:
                click(device,imsoff[0][0]+15,imsoff[0][1]+15)
            else:
                call+=1
        else:
            if imsoff:
                return True
            elif imson:
                click(device,imson[0][0]+15,imson[0][1]+15)
            else:
                call+=1

def pp4_set(device,pin='10025',ship=False,size="XS"):
    print("PP4 Set")
    call=0
    writeToDevice(device,pin)
    while True:
        if(call==10):
            break
        scr=get_screenshot(device)
        wami=where_am_i(scr)
        print(wami)
        if(wami[0]=="OU_pp_3"):
            click(device,272,910,100)
            wait_for_it(3)
        elif(wami[0]=='OU_pp_2'):
            click(device,272,925,100)
            wait_for_it(3)
        elif(wami[0]=='OU_pp_1'):
            click(device,272,910,100)
            wait_for_it(3)
        elif(wami[0]=='OU_pp_4'):
            # ims=imsearch(scr,ICONS["pp4_cp"])
            click(device,225,138)
            wait_for_it(2)
        scr=get_screenshot(device)
        wami=where_am_i(scr)
        if(wami[0]=='OU_pp_4_loc'):
            select_all_delete(device,324,297)
            paste(device)
            click(device,270,921)
            wait_for_it(5)
            break
        else:
            wait_for_it()
            call+=1
            continue
    call=0
    while True:
        if call==5:
            break
        scr = get_screenshot(device)
        imsoff = imsearch(scr,ICONS['switch_off'])
        imson = imsearch(scr,ICONS['switch_on'])
        if imson or imsoff:
            if ship:
                if imsoff:
                    click(device,imsoff[0][0],imsoff[0][1])
                    wait_for_it(2)
                scr=get_screenshot(device)
                ims=imsearch(scr,SIZE[size])
                if ims:
                    click(device,ims[0][0],ims[0][1])
                    return True
            else:
                if imson:
                    click(device,imson[0][0],imson[0][1])
                    return True
        else:
            if not ship:
                return True
            call+=1
            wait_for_it()

def OUbot(device,csv="",turn=1):
    # PUSH CSV IMDATA 1st
    if turn==3:
        return False
    INIT=ou_init(device)  ##INIT FOR POSTING 1
    if INIT:
        PP1_CLEANED = pp1_clean(device,"Weightsfosure")
        IM_ADDED = pp1_add_imgs(device)
        if(IM_ADDED):
            wait_for_it(2)
            click(device,272,925,100)
            PROCESS_PP2 = pp2_set(device,"Great Weights","3","2,4") # PROCESSING PP2 TO BE ADDED HERE
            PP2_CAT_SET = pp2_set_cat(device,cat="1,1")
            if PROCESS_PP2 and PP2_CAT_SET:
                click(device,272,925,100)
                wait_for_it(2)
                PROCESS_PP3=pp3_set(device,"135",True)
                if PROCESS_PP3:
                    click(device,272,925,100)
                    PROCESS_PP4=pp4_set(device,"10025",True,"L")
                    wait_for_it(2)
                    if PROCESS_PP4:
                        click(device,272,925,100)
                        wait_for_it(5)
                        return True
                    else:
                        return OUbot(device,csv,turn+1)
                else:
                    return OUbot(device,csv,turn+1)
            else:
                return OUbot(device,csv,turn+1)
        else:
            return OUbot(device,csv,turn+1)
    else:
        return OUbot(device,csv,turn+1)

if __name__=='__main__':
    devices = get_devices()
    print("Connected Devices:",devices)
    # csvfile=list(csv.reader(open('productdata.csv')))
    for dev in devices:
        OUbot(dev[0],1)
        