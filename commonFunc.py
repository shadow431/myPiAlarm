#!/usr/bin/python
import smtplib, yaml
from email.mime.text import MIMEText

#Get content from yaml formated file and return it as a dictionary/list
def getYaml(file):
    f = open('./'+str(file)+'.yaml','r')
    content = yaml.load(f.read())
    f.close()
    return content

settings = getYaml('settings')

#Generate and send an email
def email(message):
    msg = MIMEText(message)
    msg['Subject'] = settings['email']['subject']
    msg['From'] = settings['email']['from'] 
    msg['To'] = settings['email']['to']

    s = smtplib.SMTP(host=settings['email']['server'],port=25)
    #s.login(settings['email']['account'],settings['email']['pass'])
    s.sendmail(msg['From'],msg['To'].split(),msg.as_string())
    return s
