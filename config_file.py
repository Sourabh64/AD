import os
import configparser
from cryptography.fernet import Fernet

key = Fernet.generate_key()
print(key)
cipher_suite = Fernet(key)

password = b"mysecretpassword"
encrypted_password = cipher_suite.encrypt(password)

print(encrypted_password)

config = configparser.ConfigParser()
config.read('config.ini')

# key = os.environ['ENCRYPTION_KEY']
cipher_suite = Fernet(key)

encrypted_password = config.get('Database', 'password')
encrypted_username = config.get('Database', 'username')
port = int(config.get('Database', 'port'))
print(encrypted_password)
print(encrypted_username)
print(type(port))
print(port)
email_list = "sourabh.kulkarni@payu.in, itsupport-pan-india@payu.in, infraadmin@payu.in, ankita.mishra1@payu.in, tushar.tewatia@payu.in, cheenu.tyagi@payu.in, suresh.sharma@payu.in, bhaskar.jayanna@payu.in"
print(email_list.split(","))
email_list = email_list.split(",")
# email_list = ["sourabh.kulkarni", "kulkarni.sourabh", "sk.sk", "ks.ks"]
to_address = []
for i in email_list:
    to_address.append("<"+i+">")
print(", ".join(to_address))

