import sys
import base64
import datetime
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

def cert_load(fname):
    """Lê certificado de ficheiro PEM."""
    with open(fname, "rb") as f:
        return x509.load_pem_x509_certificate(f.read())


def cert_load_pem_bytes(pem_bytes: bytes):
    """Carrega certificado a partir de bytes PEM."""
    return x509.load_pem_x509_certificate(pem_bytes)


def cert_validtime(cert, now=None):
    """Valida que 'now' se encontra no período de validade do certificado."""
    if now is None:
        now = datetime.datetime.now(tz=datetime.timezone.utc)
    if now < cert.not_valid_before_utc or now > cert.not_valid_after_utc:
        raise x509.verification.VerificationError(
            "Certificado fora do período de validade"
        )


def cert_validsubject(cert, attrs=[]):
    """Verifica atributos do campo 'subject'.
    'attrs' é uma lista de pares (OID, valor_esperado).
    """
    for attr in attrs:
        vals = cert.subject.get_attributes_for_oid(attr[0])
        if not vals or vals[0].value != attr[1]:
            raise x509.verification.VerificationError(
                f"Subject não corresponde ao esperado: {attr}"
            )


def cert_validexts(cert, policy=[]):
    """Valida extensões do certificado.
    'policy' é uma lista de pares (OID, predicado).
    """
    for oid, pred in policy:
        ext = cert.extensions.get_extension_for_oid(oid).value
        if not pred(ext):
            raise x509.verification.VerificationError(
                f"Extensão {oid} não satisfaz a política definida"
            )


def valida_cert(cert, ca_cert, expected_cn=None):
    cert.verify_directly_issued_by(ca_cert)

    cert_validtime(cert)

    if expected_cn:
        cert_validsubject(cert, [(x509.NameOID.COMMON_NAME, expected_cn)])

    try:
        ku = cert.extensions.get_extension_for_oid(
            x509.ExtensionOID.KEY_USAGE
        ).value
        if not ku.digital_signature:
            raise x509.verification.VerificationError(
                "Certificado não autorizado para assinatura digital (KeyUsage)"
            )
    except x509.ExtensionNotFound:
        pass


def write_sig_file(sig_path: str, cert_pem: bytes, signature: bytes):
    with open(sig_path, "wb") as f:
        f.write(cert_pem)
        f.write(SEPARATOR)
        f.write(base64.b64encode(signature) + b"\n")


def read_sig_file(sig_path: str):
    with open(sig_path, "rb") as f:
        data = f.read()

    if SEPARATOR not in data:
        raise ValueError(f"Formato inválido em '{sig_path}': separador não encontrado")

    cert_pem, sig_b64 = data.split(SEPARATOR, 1)
    signature = base64.b64decode(sig_b64.strip())
    return cert_pem, signature

def sign_file(file_path: str, key_path: str, cert_path: str, password: bytes = b"1234"):
    with open(key_path, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=password)

    with open(cert_path, "rb") as f:
        cert_pem = f.read()
    cert = x509.load_pem_x509_certificate(cert_pem)

    with open(file_path, "rb") as f:
        data = f.read()

    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )

    sig_path = file_path + ".sig"
    write_sig_file(sig_path, cert_pem, signature)

    cn = cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
    cn_str = cn[0].value if cn else "(desconhecido)"
    print(f"[OK] Assinatura gerada por '{cn_str}' e gravada em '{sig_path}'")


def verify_file(file_path: str, ca_cert_path: str):
    sig_path = file_path + ".sig"

    try:
        cert_pem, signature = read_sig_file(sig_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"[ERRO] Não foi possível ler '{sig_path}': {e}")
        return False

    try:
        signer_cert = cert_load_pem_bytes(cert_pem)
        ca_cert     = cert_load(ca_cert_path)
    except Exception as e:
        print(f"[ERRO] Não foi possível carregar certificado(s): {e}")
        return False

    cn = signer_cert.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
    cn_str = cn[0].value if cn else "(desconhecido)"

    try:
        valida_cert(signer_cert, ca_cert)
    except x509.verification.VerificationError as e:
        print(f"[ERRO] Certificado de '{cn_str}' inválido: {e}")
        return False
    except Exception as e:
        print(f"[ERRO] Validação do certificado falhou inesperadamente: {e}")
        return False

    try:
        with open(file_path, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        print(f"[ERRO] Ficheiro '{file_path}' não encontrado")
        return False

    public_key = signer_cert.public_key()
    try:
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        print(f"[OK] Assinatura válida — signatário: '{cn_str}'")
        return True
    except InvalidSignature:
        print(f"[ERRO] Assinatura inválida para '{file_path}' (signatário declarado: '{cn_str}')")
        return False
    except Exception as e:
        print(f"[ERRO] Falha na verificação da assinatura: {e}")
        return False

def usage():
    print(__doc__)
    sys.exit(1)


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        usage()

    command = args[0]

    if command == "sign":
        # sign <ficheiro> <user>.key <user>.crt [password]
        if len(args) < 4:
            print("Uso: python cfich_certs.py sign <ficheiro> <user>.key <user>.crt [password]")
            sys.exit(1)
        file_path = args[1]
        key_path  = args[2]
        cert_path = args[3]
        password  = args[4].encode() if len(args) > 4 else b"1234"
        sign_file(file_path, key_path, cert_path, password)

    elif command == "verify":
        # verify <ficheiro> <CA>.crt
        if len(args) < 3:
            print("Uso: python cfich_certs.py verify <ficheiro> <CA>.crt")
            sys.exit(1)
        file_path    = args[1]
        ca_cert_path = args[2]
        ok = verify_file(file_path, ca_cert_path)
        sys.exit(0 if ok else 1)

    else:
        usage()
