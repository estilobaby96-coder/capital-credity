import os
import subprocess
import shutil

def build():
    print("Iniciando empacotamento (PyInstaller)...")
    
    # 1. Limpar diretórios de build anteriores (para evitar arquivos obsoletos)
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            print(f"Limpando pasta '{folder}'...")
            try:
                shutil.rmtree(folder)
            except Exception as e:
                print(f"Aviso: nao foi possivel apagar {folder} completamente. ({e})")
                
    import sys
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",            # Não pedir confirmação para sobrescrever a pasta dist
        "--onefile",              # Gerar um único arquivo .exe
        "--windowed",             # Não exibir a janela de terminal (console) ao abrir o app
        "--add-data", "assets;assets",  # Incluir a pasta assets no pacote (CUIDADO: no Windows é ponto-e-vírgula)
        "--collect-all", "customtkinter", # Coletar fontes e assets internos da biblioteca customtkinter
        "--name", "CapitalCredity",   # Nome do arquivo executável de saída
        "main.py"                 # Arquivo de entrada principal
    ]
    
    print("Executando comando:\n" + " ".join(cmd))
    
    # 3. Chamar o PyInstaller via subprocess
    try:
        subprocess.run(cmd, check=True)
        print("\nBuild concluido com sucesso!")
        print("O executavel esta na pasta 'dist/CapitalCredity.exe'")
        print("Lembre-se: O arquivo de banco de dados 'neto_gestor.db' sera salvo em %APPDATA%/Capital_Credity/database/")
    except subprocess.CalledProcessError as e:
        print(f"\nErro durante o build: {e}")

if __name__ == "__main__":
    build()
