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
# enter password
psswrd = input("Please enter your Secure Witness password: ")
#print ('Your input was' + " " + psswrd)
# if logged in properly then show files available
payload = {'username': usrnm, 'password': psswrd}
r = requests.post("http://infinite-plateau-9873.herokuapp.com/SecureWitness/login_decrypt/", data=payload)
print(r.text)
# if authentification failed then quit
if r.text == "unsuccessful authentication" or r.text == 'Your account has been suspended by an administrator':
    print("Exiting application...")
    sys.exit(0)

# display reports that can be downloaded
payload = {'username': usrnm, 'password': psswrd}
r = requests.post("http://infinite-plateau-9873.herokuapp.com/SecureWitness/viewReports_decrypt/", data=payload)
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
    r = requests.post("http://infinite-plateau-9873.herokuapp.com/SecureWitness/viewFiles_decrypt/", data=payload)

    #print (r.text)
    #sys.exit(0)

    #newFile = open('test.txt', 'w')
    #newFile.write(r.text)
    #newFile.close()

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
    r = requests.post('http://infinite-plateau-9873.herokuapp.com/SecureWitness/uploaded_key/', data=payload)
    #print r.text

    if r.text == "unsuccessful authentication" or r.text == 'Your account has been suspended by an administrator':
        print("Exiting application...")
        sys.exit(0)
    if r.text != "Invalid file name.":
        check = True
        #print(r.content)
        #print (r.text)

        key = RSA.importKey(r.text)


    else:
        print("File not found. Please enter a valid file name.")

# gets file to decrpy
#r = requests.get('http://127.0.0.1:5000/SecureWitness/staticfiles/' + file_enc)
payload = {'file': file_enc}
r = requests.get('https://infinite-plateau-9873.herokuapp.com/SecureWitness/uploaded_file_decrypt/'+ file_enc)
enc_data = r.content
print(enc_data)
# decrypt 
# print decrypted file contents
decrypted = key.decrypt(enc_data)
print (decrypted)

# write back descrypted to file
downloads_dir = expanduser("~/Downloads/") + file_enc

newFile = open(downloads_dir, 'w+b')
#print(decrypted.decode(encoding='utf-8'))
newFile.write(decrypted)
newFile.close()

print("File downloaded to '" + downloads_dir + "'")

