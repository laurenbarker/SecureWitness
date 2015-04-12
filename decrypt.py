#!/usr/bin/python

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random
from os.path import expanduser
import sys
import requests

# enter username

# enter password

# if logged in properly then show files available

# user enters file to decrypt 
# check if file is one displayed
file_enc = raw_input("Please enter the file you wish to decrypt: ")
print ('Your input was' + " " + file_enc)

# gets file to decrpyt
r = requests.get('http://localhost:8000/SecureWitness/uploaded_files/' + file_enc)
print r.text

# get key from db
# read in file to enc_data

# decrypt 
# print key.decrypt(enc_data) 

downloads = expanduser("~/Downloads/")

# write back descrypted to file


# not sure we need below

