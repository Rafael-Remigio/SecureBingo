import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.asymmetric import padding   
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
import base64 
from cryptography.hazmat.backends import default_backend


class Crypto:
    """Cryptographic utilities"""
 
    @classmethod
    def sym_gen(cls) -> tuple:
        """Generates a new AESGCM (key, nonce) tuple""" 
        key= AESGCM.generate_key(bit_length=128) 
        return (base64.b64encode(key).decode('ascii'), os.urandom(12))

    @classmethod
    def sym_encrypt(cls, key: bytes, data, nonce: bytes=b'12345678') -> bytes:
        """Encrypts data given with given AESGCM key"""
 
        key=base64.b64decode(key.encode('ascii'))
        data=bytes(str(data), 'ascii')
        cypher = AESGCM(key) 
        ct = cypher.encrypt(nonce, data, None)  

        return base64.b64encode(ct).decode('ascii')

    @classmethod
    def sym_decrypt(cls, key: bytes, crypted_data, nonce: bytes=b'12345678') -> bytes:
        """Decrypts encrypted data given with given AESGCM key"""
        
        crypted_data=base64.b64decode(crypted_data.encode('ascii'))
        key=base64.b64decode(key.encode('ascii'))
        cypher = AESGCM(key) 
        data = cypher.decrypt(nonce, crypted_data, None)
         
        return data.decode('ascii')

    @classmethod
    def do_hash(cls, data: bytes) -> bytes:
        """Returns an hash of a given data"""
        
        digest = hashes.Hash(hashes.SHA256()) 
        digest.update(data)    
        hash = digest.finalize().hex()
        
        return hash 

    @classmethod
    def asym_gen(cls) -> tuple:
        """Generates a new Asymetric key(Object) pair"""
        
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        return ( Crypto.serialize_private_key(private_key), Crypto.serialize_public_key(private_key.public_key()))

    @classmethod
    def asym_encrypt(cls, public_key: str, data) -> bytes:
        """Encrypts data using given public key"""
        
        public_key = Crypto.load_public_key(public_key)

        data=bytes(str(data), 'utf-8')
        ciphertext = public_key.encrypt(data,
            
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
                )
        )

        return ciphertext

    @classmethod
    def asym_decrypt(cls, private_key: str, crypted_data) -> bytes:
        """Encrypts data using given private key"""

        private_key = Crypto.load_private_key(private_key)
        
        crypted_data=bytes(str(crypted_data), 'utf-8')
        data = private_key.decrypt(crypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        return data

    @classmethod
    def sign(cls, private_key: str, data) -> bytes:
        """Returns Signature of given data signed with given private key"""
          
        private_key = Crypto.load_private_key(private_key)

        data=bytes(str(data), 'utf-8')
        signature = private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return signature

    @classmethod
    def verify(cls, public_key: str, message, signature: bytes) -> bool:
        """Verifies if given message matches with given signature"""
          
        public_key = Crypto.load_public_key(public_key)

        message =message.encode()
        try:  
            public_key.verify(
                signature,
                message,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            ) 
        except InvalidSignature:
            return False
        except:
            print("Unidentified Error")
            return False

        return True


    @classmethod
    def verifyFromCard(cls, public_key: bytes, message, signature: bytes) -> bool:
        """Verifies if given message matches with given signature"""

        public_key = Crypto.load_public_key(public_key.decode('ascii'))

        hash_function = hashes.SHA256()
        signed_data_hash = hashes.Hash(hash_function, default_backend())
        signed_data_hash.update(str(message).encode('utf-8'))
        signed_data_hash = signed_data_hash.finalize()

        try:  
            public_key.verify(
                signature,
                signed_data_hash,
                padding.PKCS1v15(),
                hashes.SHA256()
            ) 
        except InvalidSignature:
            return False
        except:
            print("Unidentified Error")
            return False

        return True


    @classmethod
    def load_private_key(cls, key_string: str):
        """ """ 
        key_object = serialization.load_pem_private_key(key_string.encode(), password=b'mypassword')
        return  key_object
    @classmethod
    def load_public_key(cls, key_string: str):
        """ """  
        key_object = serialization.load_pem_public_key(key_string.encode())
        return  key_object
    @classmethod
    def serialize_public_key(cls, key_object) -> str:
        """ """ 
        key_string = key_object.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ) 
        return key_string.decode() 
    @classmethod
    def serialize_private_key(cls, key_object) -> str:
        """ """ 
        key_string = key_object.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(b'mypassword')
        )
        return key_string.decode()  
 