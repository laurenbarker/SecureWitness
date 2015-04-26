#!/usr/local/bin/python3

from Crypto.PublicKey import RSA
from Crypto import Random
from os.path import expanduser
import sys
import requests
import getpass
from os.path import expanduser

# enter username
usrnm = input("Please enter your Secure Witness username: ")
# print ('Your input was' + " " + usrnm)
# enter password
psswrd = getpass.getpass("Please enter your Secure Witness password: ")
#print ('Your input was' + " " + psswrd)

# if logged in properly then show files available
payload = {'username': usrnm, 'password': psswrd}
r = requests.post("http://127.0.0.1:5000/SecureWitness/login_decrypt/", data=payload)
print(r.text)
# if authentification failed then quit
if r.text == "unsuccessful authentication" or r.text == 'Your account has been suspended by an administrator':
    print("Exiting application...")
    sys.exit(0)

# display reports that can be downloaded
payload = {'username': usrnm, 'password': psswrd}
r = requests.post("http://127.0.0.1:5000/SecureWitness/viewReports_decrypt/", data=payload)
print("Reports you have access to:")
print(r.text)
if r.text == "unsuccessful authentication":
    print("Exiting application...")
    sys.exit(0)

check = False
while check == False:
    # display files that can be downloaded in specified report
    rpt = input("Please enter the report number you would like to view: ")
    payload = {'username': usrnm, 'password': psswrd, 'report': rpt}
    r = requests.post("http://127.0.0.1:5000/SecureWitness/viewFiles_decrypt/", data=payload)
    if r.text == "unsuccessful authentication":
        print("Exiting application...")
        sys.exit(0)
    if r.text != "Report not found.":
        check = True
        data = r.text.split("\t")
        print("Report: " + data[0])
        print("Author: " + data[1])
        print("Short Description: " + data[2])
        print("Long Description: " + data[3])
        print("Loation: " + data[4])
        print("Keywords: " + data[5])
        print("Date: " + data[6])
        print("File: " + data[7])
    else:
        print("Report not found. Please enter a valid report.")

check = False
while check == False:
    # user enters file to decrypt
    file_enc = input("Please enter the file you wish to decrypt: ")
    #print ('Your input was' + " " + file_enc)
    print("")

    # check if user has access via django server and get key to decrypt
    payload = {'username': usrnm, 'password': psswrd, 'report': rpt, 'file': file_enc}
    r = requests.post('http://127.0.0.1:5000/SecureWitness/uploaded_key/', data=payload)
    #print r.text

    if r.text == "unsuccessful authentication" or r.text == 'Your account has been suspended by an administrator':
        print("Exiting application...")
        sys.exit(0)
    if r.text != "Invalid file name.":
        check = True
        #print(r.content)
        key = RSA.importKey(r.content)


    else:
        print("File not found. Please enter a valid file name.")

# gets file to decrpyt
r = requests.get('http://127.0.0.1:5000/SecureWitness/uploaded_files/' + file_enc)
enc_data = r.content

# decrypt 
# print decrypted file contents
decrypted = key.decrypt(enc_data)
#print decrypted

# write back descrypted to file
downloads_dir = expanduser("~/Downloads/") + file_enc

newFile = open(downloads_dir, 'w')
newFile.write(decrypted)
newFile.close()

print("File downloaded to '" + downloads_dir + "'")

