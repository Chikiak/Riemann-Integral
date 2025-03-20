import customtkinter as ctk
from ui import InteractiveApp

if __name__ == "__main__":
    """
    Punto de entrada principal de la aplicación.
    Crea la ventana raíz e inicializa la aplicación.
    """
    # Crear ventana principal
    root = ctk.CTk()

    # Inicializar la aplicación
    app = InteractiveApp(root)

    # Iniciar el bucle principal de la interfaz
    root.mainloop()