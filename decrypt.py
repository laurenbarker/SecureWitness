#!/usr/bin/python

from Crypto.PublicKey import RSA
from Crypto import Random
from os.path import expanduser
import sys
import requests
from base64 import b64decode

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
#r = requests.get('http://localhost:8000/SecureWitness/uploaded_key/', data=payload)
#print r.text

# gets file to decrpyt
r = requests.get('http://localhost:8000/SecureWitness/uploaded_files/' + file_enc)
#r = requests.get('http://localhost:8000/SecureWitness/login')
enc_data = r.content

# read in file to enc_data
#print enc_data

# decrypt 
#key = RSA.importKey('-----BEGIN RSA PRIVATE KEY-----\nMIICWwIBAAKBgQCf901HMLoWb66tfraAJMpNONVYDFpDQp52TaFEovQ1xMV5zaueGO7XrsjuU0a6qmap6VOf3vZPVUck62kbrZqUqh8RJfNKxqnYWNxCfAo9Drvq7eSYLhLfCqr6bG46cSbPreuV0u79ppNITwWKOK3LNX4XhqImENl1LzTzjSnROwIDAQABAoGAPj8fRRqC7wQadsyd+5NVXWNGMXLtFMsxmltu66R1Xw7owRL1Oxn8ptUOvx6MoUp5lJiEv+sk8Y3/lzA7wFd3lNBzsSlkQurQJmKf/uHTQUmJv0Wp0IKM8czaB+bP0n27Fm51wVRvViutRZ8YRCq72g3BEIRT7SeaRZs6fSkNc9ECQQDHVfEiOZdGngq6PrrO/JO5x2fTA9uHSAqhhc3WEtGDjjsxppFYcoa04j5cnyZNDiwVvWmo4PobK1/HNHoKdh1PAkEAzXBZXP4uI4+3WLlXZJg4gxTT5nJAkqkjIlX5M8Msj72uMDdymR3lhGs39ZfjHglMWeJOIDRbm1cEqsvt+yMKVQJAAPYNH5kffZuteZBr3iuhmre3bHEMUe6q/nRitbGJiRTafDbNZJvIwn6ExnWN/bkfxUsQg1vyWMcwwwkhvYMsSQJADgy679MqUKBJh7XVNjn602wfOclihSUwE+8RRer5JzNvsDh6i+IxiibTAubKT4mPQS5q7WTnRu5ikVO1CNHSqQJAb6p+/6eQE7aSfKx3cjbBcS468huR8MRzF8dWmPqihtILaMNtHeGeGrEhH7sXjn+bXh3gPTESuJ8ugWQcYQezLw==\n-----END RSA PRIVATE KEY-----')
key = RSA.importKey('-----BEGIN RSA PRIVATE KEY-----\nMIICXQIBAAKBgQChT//syWSzbJzmaG64qkrdSdqec7z8AjkjNVo6RAeitOlI5OIwbqBG6eBsGwjBLwGn/l/xNQwfac51AZ5qTpDRGO3TTtQYUs58c0RhE7uobN8rOQmRahu66xChlmKfWta1jGLwLvBuog4UZHmtaaGDLBLQ+68zjh17fOk7hkG9kwIDAQABAoGAQBKVlci8nePjQkVyzRie2dyO4GcaRoLfjROQ/hmtarwu+Qwop5IZSXF1+ZqXVJxGLSMFmro2UXfmUGVPNex06ma97GGsrabBjdHMsCdW2WUhlfHFwop5vXGFOdWh5ZMREA46LZY9WpJWC0WzKa5mAPzoL/H9iYE717CA0KpkjSECQQC5YWAsmvzUbIBCXvRCh7YGUJG8/kK6E9UePvo0dWyOGLomrUzEixLljkTfVzN7Nsd87vgfytzIt5oPtu/fSAhxAkEA3sN7Y4NkufUr3WWbgsN0FmCLT0LW3NVwIOqZrLrYGOJCkPL/Rl99MjOT9xyF0Mx5Ret1PATMKrp/Ktk0KmQIQwJBAI8daOUmxhesqBwVOFeAc/tOCiUw2gzTsM1H61vCZ4sP9e5UDhcSEwWbnvoZVQpDkSCXUIEi2O4wKEUHgwoKj1ECQQCEOtllartBvwy4sPWsm0Sve8N12yEbmP6kK13pMEfSDYyh6fwp08jHIeK1DpNIK/fYzzmZ1Oc0fdu6nY/fkd1tAkBZYXbllfjt8aOdETg/cQSaAeEDIKFnw8gnXE1puoz28wLONZ0W9DB8lcD8NBNrNUsPHyo+dgqa2nhX1zioe7gA\n-----END RSA PRIVATE KEY-----')
#print key
print key.decrypt(enc_data) 


# write back descrypted to file

