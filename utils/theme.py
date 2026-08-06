import customtkinter as ctk

def apply_theme():
    """Applies the default visual theme for the application."""
    # O user pediu tema escuro corporativo com verde moderno
    ctk.set_appearance_mode("Dark")
    
    # CustomTkinter oferece temas integrados (blue, dark-blue, green)
    # Aqui usaremos "green" como base para combinar com o verde corporativo, 
    # e poderemos criar um json de tema customizado no futuro se necessário.
    ctk.set_default_color_theme("green")
