import sys,yaml

settings = {}

print "Server:"
settings['master'] = raw_input()
print "How offten should slaves check in?:"
settings['checkinTime'] = int(raw_input())

settings['email'] = {}

print "Send emails from:"
settings['email']['from'] = raw_input()

print "SMTP username:"
settings['email']['account'] = raw_input()
print "SMTP password:"
settings['email']['pass'] = raw_input()
print "SMTP server"
settings['email']['server'] = raw_input()
print "Email Subject?:"
settings['email']['subject'] = raw_input()
print "Send emails TO?:"
settings['email']['to'] = raw_input()

file = open('settings.yaml', 'w')
file.write(yaml.dump(settings))
file.close()
