#!/usr/bin/python

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random
from os.path import expanduser
import sys
import requests

# user enters file to decrypt
file_enc = raw_input("Please enter the file you wish to decrypt: ")
print ('Your input was' + " " + file_enc)

r = requests.get('http://localhost:8000/SecureWitness/uploaded_files/' + file_enc)
print r.text

# get key from db
# read in file to enc_data

# decrypt 
#print key.decrypt(enc_data) 

downloads = expanduser("~/Downloads/")

# write back descrypted to file


# not sure we need below

