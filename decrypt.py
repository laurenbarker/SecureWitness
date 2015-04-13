#!/usr/bin/python

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random
from os.path import expanduser
import sys
import requests

# enter username
usrnm = raw_input("Please enter your Secure Witness username: ")
print ('Your input was' + " " + usrnm)
# enter password
psswrd = raw_input("Please enter your Secure Witness password: ")
print ('Your input was' + " " + psswrd)

# if logged in properly then show files available
payload = {'username': usrnm, 'password': psswrd}
r = requests.post("http://localhost:8000/SecureWitness/login_decrypt/", data=payload)
print(r.text)


# user enters file to decrypt 
# check if file is one displayed
file_enc = raw_input("Please enter the file you wish to decrypt: ")
print ('Your input was' + " " + file_enc)

# gets file to decrpyt
#r = requests.get('http://localhost:8000/SecureWitness/uploaded_files/' + file_enc)
r = requests.get('http://localhost:8000/SecureWitness/login')
print r.text




# get key from db
# read in file to enc_data

# decrypt 
# print key.decrypt(enc_data) 

downloads = expanduser("~/Downloads/")

# write back descrypted to file


# not sure we need below

