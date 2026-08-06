import os
import sys

def get_resource_path(relative_path: str) -> str:
    """
    Retorna o caminho absoluto do recurso, compatível com ambiente dev e PyInstaller.
    """
    try:
        # PyInstaller cria um diretório temporário e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Em desenvolvimento, pega o diretório atual do projeto (assumindo que seja executado da raiz do projeto)
        # O diretório base deve ser o pai da pasta utils
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    return os.path.join(base_path, relative_path)
