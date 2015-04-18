#!/usr/bin/python

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
# if authentification failed then quit
if r.text == "unsuccessful authentication" or r.text == 'Your account has been suspended by an administrator':
	print "Exiting application..."
	sys.exit(0)

# display files that can be downloaded
payload = {'username': usrnm}
r = requests.post("http://localhost:8000/SecureWitness/viewFiles_decrypt/", data=payload)
print "Reports you have submitted:"
print(r.text)

# user enters file to decrypt 
file_enc = raw_input("Please enter the file you wish to decrypt: ")
print ('Your input was' + " " + file_enc)

# check if user has access via django server and get key to decrypt

# gets file to decrpyt
r = requests.get('http://localhost:8000/SecureWitness/uploaded_files/' + file_enc)
#r = requests.get('http://localhost:8000/SecureWitness/login')
print r.text

# read in file to enc_data

# decrypt 
# print key.decrypt(enc_data) 


# write back descrypted to file

