import pandas as pd
import requests
from bs4 import BeautifulSoup as bs4
from datetime import datetime
import smtplib

##TODO refactor to OOP

headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}

def loadTargets(excel):
    ''' Reads csv '''
    df = pd.read_csv(excel, sep = ';', encoding = "ISO-8859-1")
    return df

def getPage(url):
    ''' Transforms URL into html code'''
    response = requests.get(url, headers = headers)
    content = response.content
    soup = bs4(content, 'html.parser')
    return soup

def getSizesData(soup):
    ''' Checks which sizes are available '''
    d = {'Available':[], 'Unavailable': []}
    for i in soup.findAll(class_ ='product-size'):
        i = str(i)
        size = i[i.find("data-name") + 11: i.find("data-sku") - 2].strip()
        disabled = i.find('disabled')

        if disabled == -1:
            d['Available'].append(size)
        else:
            d['Unavailable'].append(size)
    return d

def searchForItems(dataframe):
    ''' Checks if wanted size is available and sends an Email '''
    MESSAGE = ''

    for index, value in dataframe.iterrows():
        scouted_url = value['URL']
        scouted_size = value['SIZE']
        scouted_name = value['NAME']

        html = getPage(scouted_url)
        results = getSizesData(html)

        if scouted_size.upper() in results['Available']:
            single_message = '{} HAS BEEN FOUND, SIZE - {}, LINK - {}.'.format(scouted_name, scouted_size, scouted_url)
            print(single_message)
            MESSAGE = MESSAGE + '\n' + single_message + '\n'
        #print(results)
    return MESSAGE

def getCredentials(txtPath):
    ''' Gets credentials for gmail '''
    with open(txtPath) as file:
        lines = file.readlines()
        sender_email = lines[0]
        password = lines[1]
        rec_email = lines[2]
        return sender_email, password, rec_email
        
def sendMessage(email_text, sender_email,rec_email,password):

    SUBJECT = 'Sizes available'
    message = 'Subject: {}\n\n{}'.format(SUBJECT, email_text)

    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()

    server.login(sender_email,password)
    server.sendmail(sender_email, rec_email, message.encode('utf-8'))


df = loadTargets('targets.csv')
sender_email, password, rec_email = getCredentials('WATCHER_AUTH.txt')

previous_msg = ''
while True:
    #Added try
    print("Current Time =", datetime.now().strftime("%H:%M:%S"))
    try:
        msg = searchForItems(df)

        if len(msg) > 1 and msg != previous_msg:
            sendMessage(msg, sender_email, rec_email, password)
            print('Email sent')
            previous_msg = msg
        print('msg :',len(msg),'prev :', len(previous_msg))
    except:
        pass




