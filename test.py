from Crypto.PublicKey import RSA
from Crypto import Random

text = b'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
random_generator = Random.new().read
key = RSA.generate(1024, random_generator)
public_key = key.publickey()
enc_data = public_key.encrypt(text[0:], 32)[0]
#enc_data += public_key.encrypt(text[128:len(text) - 1], 32)[0]
pkey = key.exportKey('PEM')


# for x in range(0,len(enc_data),127):
print(RSA.importKey(pkey).decrypt(enc_data[0:]))

#print(decrypted)