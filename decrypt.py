#!/usr/bin/python

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto import Random
from os.path import expanduser
import sys

# user enters file to decrypt
file_enc = input('Please enter the file you wish to decrypt: ')


# get key from db
# read in file to enc_data

# decrypt 
print key.decrypt(enc_data) 

downloads = expanduser("~/Downloads/")

# write back descrypted to file


# not sure we need below

#sign
text = 'abcdefgh'
hash = SHA256.new(text).digest()
print hash
signature = key.sign(hash, '')
print signature

#verify
text = 'abcdefgh'
hash = SHA256.new(text).digest()
print hash
print public_key.verify(hash, signature)
