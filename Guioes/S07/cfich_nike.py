import os,sys
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def mkpair(x, y):
   """ produz uma byte-string contendo o tuplo '(x,y)' ('x' e 'y' são byte-strings) """
   len_x = len(x)
   len_x_bytes = len_x.to_bytes(2, 'little')
   return len_x_bytes + x + y

def unpair(xy):
   """ extrai componentes de um par codificado com 'mkpair' """
   len_x = int.from_bytes(xy[:2], 'little')
   x = xy[2:len_x+2]
   y = xy[len_x+2:]
   return x, y

def enc_AES_GCM(key,mensagem, aad):
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, mensagem, aad)
    return nonce + ct 

def dec_AES_GCM(key,mensagem, aad):
    nonce = mensagem[0:12]
    ct = mensagem[12:]

    aesgcm = AESGCM(key) 
    mensagem_original = aesgcm.decrypt(nonce, ct, aad)
    return mensagem_original

def cfich_nike(argv):
    comando = argv[1]
    p = 0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF
    g = 2
    aad = b"authenticated but unencrypted data"

    if comando == 'setup':
        if len(argv) != 3:
            print('python cfich_nike.py setup <user>')
            sys.exit(1)
        
        user = argv[2]

        parameters = dh.DHParameterNumbers(p, g).parameters()
        chave_privada = parameters.generate_private_key()
        chave_publica = chave_privada.public_key()

        sk = chave_privada.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        pk = chave_publica.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        with open(f'{user}.pk', 'wb') as file:
            file.write(pk)

        with open(f'{user}.sk', 'wb') as file:
            file.write(sk)
        
    elif comando == 'enc':
        
        if len(argv) != 4:
            print('python cfich_nike.py enc <user> <fich>')
            sys.exit(1)

        user = argv[2]
        ficheiro = argv[3]

        with open(f'{user}.pk', 'rb') as file:
            public_pem_data = file.read()
        
        bob_public = serialization.load_pem_public_key(public_pem_data)

        parameters = bob_public.parameters()
        alice_priv = parameters.generate_private_key()
        alice_public = alice_priv.public_key()

        shared_secret = alice_priv.exchange(bob_public)
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=None,
        ) 

        k = hkdf.derive(shared_secret)

        with open(ficheiro, 'rb') as file:
            mensagem = file.read()

        mensagem_cifrada = enc_AES_GCM(k, mensagem, aad)

        pk_alice = alice_public.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        packed = mkpair(pk_alice, mensagem_cifrada)
    
        with open(ficheiro + '.enc', 'wb') as file:
            file.write(packed)
        
    elif comando == 'dec':

        if len(argv) != 4:
            print('python cfich_nike.py dec <user> <fich>')
            sys.exit(1)
        
        user = argv[2]
        cripto_ficheiro = argv[3]

        with open(cripto_ficheiro, "rb") as f:
            packed = f.read()
        
        try:
            with open(f'{user}.sk', 'rb') as f:
                sk_bob = f.read()
        except:
            print(f'O ficheiro "{user}.sk" não existe!')
            sys.exit(1)

        pk_alice, mensagem_cifrada = unpair(packed)

        bob_priv = serialization.load_pem_private_key(sk_bob, password=None)
        alice_pub = serialization.load_pem_public_key(pk_alice)
        
        shared_secret = bob_priv.exchange(alice_pub)
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=None,
        ) 

        k = hkdf.derive(shared_secret)

        mensagem_original = dec_AES_GCM(k,mensagem_cifrada, aad)

        mensagem_final = cripto_ficheiro.replace('.enc', '.dec')
        with open(mensagem_final,'wb') as f:
            f.write(mensagem_original)

if __name__ == "__main__":
    cfich_nike(sys.argv) 
