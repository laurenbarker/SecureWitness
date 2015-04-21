#!/usr/bin/python

from Crypto.PublicKey import RSA
from Crypto import Random
from os.path import expanduser
import sys
import requests
import getpass
# TODO: add parameters to requests that check to see it you are logged in on the server side

# enter username
usrnm = raw_input("Please enter your Secure Witness username: ")
#print ('Your input was' + " " + usrnm)
# enter password
psswrd = getpass.getpass("Please enter your Secure Witness password: ")
#print ('Your input was' + " " + psswrd)

# if logged in properly then show files available
payload = {'username': usrnm, 'password': psswrd}
r = requests.post("http://localhost:8000/SecureWitness/login_decrypt/", data=payload)
print(r.text)
# if authentification failed then quit
if r.text == "unsuccessful authentication" or r.text == 'Your account has been suspended by an administrator':
	print "Exiting application..."
	sys.exit(0)

# display reports that can be downloaded
payload = {'username': usrnm, 'password': psswrd}
r = requests.post("http://localhost:8000/SecureWitness/viewReports_decrypt/", data=payload)
print "Reports you have submitted:"
print(r.text)
if r.text == "unsuccessful authentication":
	print "Exiting application..."
	sys.exit(0)

# display files that can be downloaded in specified report
rpt = raw_input("Please enter the report name you would like to view: ")
payload = {'username': usrnm, 'password': psswrd, 'report': rpt}
r = requests.post("http://localhost:8000/SecureWitness/viewFiles_decrypt/", data=payload)
print "Report:" + "\t" + "Author:" + "\t" + "Short Description:" + "\t" + "Long Description:" + "\t" +"Loation:" + "\t" + "Keywords:" + "\t" + "Date:" + "\t" + "File:"
print(r.text)
if r.text == "unsuccessful authentication":
	print "Exiting application..."
	sys.exit(0)

# user enters file to decrypt 
# TODO: add password parameter
file_enc = raw_input("Please enter the file you wish to decrypt: ")
print ('Your input was' + " " + file_enc)

# check if user has access via django server and get key to decrypt
payload = {'username': usrnm, 'password': psswrd, 'report': rpt, 'file': file_enc}
r = requests.post('http://localhost:8000/SecureWitness/uploaded_key/', data=payload)
#print r.text
if r.text == "unsuccessful authentication" or r.text == 'Your account has been suspended by an administrator':
	print "Exiting application..."
	sys.exit(0)
key = RSA.importKey(r.text)

# gets file to decrpyt
r = requests.get('http://localhost:8000/SecureWitness/uploaded_files/' + file_enc)
#r = requests.get('http://localhost:8000/SecureWitness/login')
enc_data = r.content

# decrypt 

#print key
print key.decrypt(enc_data) 


# write back descrypted to file

