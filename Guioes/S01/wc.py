import sys

def main(inp):
    n_lines = 0
    n_words = 0
    n_char = 0

    ficheiro = inp[1]

    lista = [
        "[", "]", "{", "}", "(",'"', "'", "«", "»",
        "+", "-", "*", "/", "=", ">", "@", "#", "$", "%", "&", "|", 
        "_", "→", "©", "®"
        ]
    
    with open(ficheiro, "r") as file:
        for linha in file:
            n_lines += 1
            lista_palavras = linha.split()
            for palavra in lista_palavras:
                n_char += len(palavra)
                if palavra not in lista:
                    n_words += 1
    
    print(f"Number of Lines: {n_lines}")
    print(f"Number of Words: {n_words}")
    print(f"Number of Char: {n_char}")

if __name__ == "__main__":
    main(sys.argv)