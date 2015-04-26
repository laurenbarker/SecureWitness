from Crypto.PublicKey import RSA
from Crypto import Random
text = b'n3#d74ff0ee8da3b9806b18c877dbf29bbde50b5bd8e4dad7a3a725000feb82e8f1#thef374+++@@----!@#!#$%!#$(*(*(&@#(*(@#######################'
random_generator = Random.new().read
key = RSA.generate(1024, random_generator)
public_key = key.publickey()
enc_data = public_key.encrypt(text,32)
pkey = key.exportKey('PEM')
decrypted = RSA.importKey(pkey).decrypt(enc_data)

print(decrypted)