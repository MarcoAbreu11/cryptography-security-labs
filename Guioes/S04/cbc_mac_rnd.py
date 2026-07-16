import sys, os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms
from cryptography.hazmat.primitives.ciphers.modes import CBC

class InvalidTag(Exception):
    pass

def cbc_mac(argv):
    comando = argv[1]
    key_input = argv[2].encode()
    
    if len(key_input) < 32:
        key = key_input + bytes(32 - len(key_input))
    elif len(key_input) > 32:
        key = key_input[:32] 
    else:
        key = key_input
    
    if len(argv) == 4 and comando == "tag": 
        file_name = argv[3]

        iv = os.urandom(16)
        with open(file_name, 'rb') as file:
            mensagem = file.read()
            
        resto = len(mensagem) % 16
        if resto != 0:
            mensagem += bytes(16 - resto)
        
        algorithm = algorithms.AES(key)
        cipher = Cipher(algorithm, mode=CBC(iv))
        encryptor = cipher.encryptor()
        ct = encryptor.update(mensagem) + encryptor.finalize()
        tag_calculada = ct[-16:]

        with open(file_name + '.tag', 'wb') as file:
            file.write(iv + tag_calculada)

    elif len(argv) == 5 and comando == "verify":
        file_name = argv[3] 
        tag_file = argv[4] 

        with open(file_name, 'rb') as file:
            mensagem = file.read()
            
        resto = len(mensagem) % 16
        if resto != 0:
            mensagem += bytes(16 - resto)

        with open(tag_file, 'rb') as file:
            iv_e_tag = file.read()

        if len(iv_e_tag) != 32:
            print("Ficheiro de tag corrompido ou inválido.")
            sys.exit(1)

        iv = iv_e_tag[0:16]
        tag = iv_e_tag[16:]

        algorithm = algorithms.AES(key)
        cipher = Cipher(algorithm, mode=CBC(iv))
        encryptor = cipher.encryptor()
        ct = encryptor.update(mensagem) + encryptor.finalize()
        tag_calculada = ct[-16:]

        if tag != tag_calculada:
            raise InvalidTag()
        else:
            print('Tag válido')
            sys.exit(1)
    else:
        print('python cbc_mac_rnd.py tag <key> <file>')
        print('python cbc_mac_rnd.py verify <key> <file> <tag>') 
        sys.exit(1)
    
if __name__ == "__main__":
    try:
        cbc_mac(sys.argv)
    except InvalidTag:
        print("InvalidTag")
        sys.exit(1)