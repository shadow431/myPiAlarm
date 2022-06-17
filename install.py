import sys,yaml

settings = {}

print("Server:")
settings['master'] = input()
print("How offten should slaves check in?:")
settings['checkinTime'] = int(input())

settings['email'] = {}

print("Send emails from:")
settings['email']['from'] = input()

print("SMTP username:")
settings['email']['account'] = input()
print("SMTP password:")
settings['email']['pass'] = input()
print("SMTP server")
settings['email']['server'] = input()
print("Email Subject?:")
settings['email']['subject'] = input()
print("Send emails TO?:")
settings['email']['to'] = input()

file = open('settings.yaml', 'w')
file.write(yaml.dump(settings))
file.close()
