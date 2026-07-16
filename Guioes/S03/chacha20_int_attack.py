import sys

def colocar_mesmo_tamanho(newPtxtAtPos,ptxtAtPos):
    t_antigo = len(ptxtAtPos)
    t_novo = len(newPtxtAtPos)

    l = []
    for i in range(t_antigo):
        l.append(' ')
    
    for i in range(t_novo):
        l[i] = newPtxtAtPos[i]
    
    str_final = ""
    for a in l:
        str_final += a
    return str_final 

def cha_cha20_attack(mensagem_criptografada, ptxtAtPos, newPtxtAtPos, pos):
    for i in range(len(ptxtAtPos)):
        mensagem_criptografada[pos+i] = mensagem_criptografada[pos+i] ^ (ptxtAtPos[i] ^ newPtxtAtPos[i])
    return mensagem_criptografada

def cha_cha20_preparacao(argv):
    if len(argv) != 5:
        print("python chacha20_int_attack.py fctxt pos ptxtAtPos newPtxtAtPos")
        sys.exit(1)
    
    ficheiro_com_criptograma = argv[1]
    with open(ficheiro_com_criptograma, "rb") as file:
        mensagem_criptografada = bytearray(file.read())
    
    pos = int(argv[2])
    ptxtAtPos = argv[3]
    newPtxtAtPos = argv[4]

    if len(newPtxtAtPos) < len(ptxtAtPos):
        nova_string = colocar_mesmo_tamanho(newPtxtAtPos,ptxtAtPos)
        mensagem_criptografada = cha_cha20_attack(mensagem_criptografada, ptxtAtPos.encode(), nova_string.encode(), pos)
    elif len(newPtxtAtPos) == len(ptxtAtPos):
        mensagem_criptografada = cha_cha20_attack(mensagem_criptografada, ptxtAtPos.encode(), newPtxtAtPos.encode(), pos)
    else:
        print("A nova palavra deve ter o mesmo tamanho ou menor da antiga!")
        sys.exit(1) 

    with open(ficheiro_com_criptograma + '.attck', "wb") as file:
        file.write(bytes(mensagem_criptografada))
 
if __name__ == "__main__":
    cha_cha20_preparacao(sys.argv)