import os,sys,struct
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def enc_aes_gcm(key, aad, mensagem):
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ct = aesgcm.encrypt(nonce, mensagem, aad)
    return nonce + ct

def pbenc_aes_gcm(argv):
    if len(argv) != 3:
        print("python pbenc_aes_gcm.py enc <ficheiro>")
        print("python pbenc_aes_gcm.py dec <ficheiro>")
        sys.exit(1)
    
    comando = argv[1]
    fich = argv[2]

    pass_phrase = input('Digite a pass: ').encode()

    if comando == 'enc':
        with open(fich,'rb') as file:
            mensagem = file.read()
        
        aad = input('Digite o aad: ').encode()

        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=1_200_000,
        )
        key = kdf.derive(pass_phrase)

        mensagem_enc = enc_aes_gcm(key,aad,mensagem)
        tamanho_add = struct.pack('I',len(aad))

        with open(fich + '.enc', 'wb') as file:
            file.write(tamanho_add + salt + aad + mensagem_enc)
        
    elif comando == 'dec':
        with open(fich,'rb') as file:
            mensagem_enc = file.read()
        
        tamanho_add = struct.unpack('I', mensagem_enc[0:4])[0]

        salt = mensagem_enc[4:20]
        aad = mensagem_enc[20:20+tamanho_add]
        nonce = mensagem_enc[20+tamanho_add:32+tamanho_add]
        ct = mensagem_enc[32+tamanho_add:]

        try:
            kdf = PBKDF2HMAC( 
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=1_200_000,
            ) 
            key = kdf.derive(pass_phrase)

            aesgcm = AESGCM(key)
            mensagem = aesgcm.decrypt(nonce, ct, aad)

            fich_final = fich.replace('.enc','.dec')  
            with open(fich_final, 'wb') as file:
                file.write(mensagem) 
        except:
            print('Senha incorreta ou dados corrompidos')
            sys.exit(1)

if __name__ == "__main__":
    pbenc_aes_gcm(sys.argv)
