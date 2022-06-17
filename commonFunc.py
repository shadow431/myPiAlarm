#!/usr/bin/python
import smtplib, yaml
from email.mime.text import MIMEText

#Get content from yaml formated file and return it as a dictionary/list
def getYaml(file):
    with open(r'./{}.yaml'.format(str(file))) as yaml_file:
      content = yaml.load(yaml_file, Loader=yaml.FullLoader)

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
