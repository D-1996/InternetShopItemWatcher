import numpy as np
import cv2
from selenium import webdriver
from PIL import ImageGrab
from time import sleep
import pandas as pd
import smtplib

WINDOW_SIZE = "1920,1080"

XS = cv2.imread('XS_black.png')
S = cv2.imread('S_black.png')
M = cv2.imread('M_black.png')
L = cv2.imread('L_black.png')
XL = cv2.imread('XL_black.png')
XXL = cv2.imread('XXL_black.png')

sizes = [XS,S,M,L,XL,XXL]
sizes_str = ['XS','S','M','L','XL','XXL']

options = webdriver.ChromeOptions()
options.add_argument("headless")
options.add_argument("--window-size=%s" % WINDOW_SIZE)
options.add_experimental_option('excludeSwitches',['enable-logging'])


threshold = .99
browser = webdriver.Chrome(options=options)

f=open("auth.txt","r")
lines = f.readlines()
sender_email = lines[0]
rec_email = lines[1]
password = lines[2]
f.close()


watchlist = pd.read_csv('watchlist.csv', sep = ';')

def check_for_sizes(scouted_size,img_rgb):
    available = []
    for i, v in enumerate(sizes):
    
        name = sizes_str[i]
        template = v
        w, h = template.shape[:-1]
        res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)

        if loc[0].size != 0:
            available.append(name)
            
    if scouted_size in available:
        return 'Dostępny szukany rozmiar : {}'.format(scouted_size)
     

def gmailer(email_text,sender_email,rec_email,password):

    SUBJECT = 'Sizes available'
    message = 'Subject: {}\n\n{}'.format(SUBJECT, email_text)

    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()

    server.login(sender_email,password)
    server.sendmail(sender_email, rec_email, message.encode('utf-8'))

def work_on_browser():
    message = ''
    for i,v in watchlist.iterrows():
        browser.get(v[1])
        product_name = browser.find_element_by_css_selector('#product > div.product-info-container._product-info-container > div > div.info-section > header > h1')
        browser.save_screenshot('snapshot.png')
        screen = cv2.imread('snapshot.png')
        img_rgb = np.array(screen)
        scouted_size_available = check_for_sizes(v[0],img_rgb)
        if scouted_size_available == None:
            pass
        else:
            message = message + '{} / {} / {} \n'.format(product_name.text, v[1], scouted_size_available)    
    return message

def watch():
    message = work_on_browser()
    print(message)
    print(len(message))
    if len(message)!=0:
        gmailer(message,sender_email,rec_email,password)
    else:
        pass


#test for 20 minutes
for i in range(1):
    watch()
    #sleep(120)
browser.close()
browser.quit()
    

