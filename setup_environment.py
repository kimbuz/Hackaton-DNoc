import subprocess
import sys

def install_compatible_versions():
    """Instala versiones compatibles de las dependencias"""
    
    packages = [
        "urllib3==1.26.18",
        "boto3==1.34.0",
        "botocore==1.34.0"
    ]
    
    for package in packages:
        print(f"Instalando {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("✅ Dependencias instaladas correctamente")

if __name__ == "__main__":
    install_compatible_versions()