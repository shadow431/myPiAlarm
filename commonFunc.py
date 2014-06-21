#!/usr/bin/python
import smtplib, yaml
from email.mime.text import MIMEText

settings = getYaml('settings')

#Functions needed by Both master and Slave

def email(message):
    msg = MIMEText(message)
    msg['Subject'] = settings['email']['subject']
    msg['From'] = settings['email']['from'] 
    msg['To'] = settings['email']['to']

    s = smtplib.SMTP_SSL(settings['email']['server'])
    s.login(settings['email']['account'],settings['email']['pass'])
    s.sendmail(msg['From'],[msg['To']],msg.as_string())
    return s

def getYaml(file):
    f = open('./'+str(file)+'.yaml','r')
    content = yaml.load(f.read())
    f.close()
    return content

