import tkinter as tk
from gui import ChatBotGUI
import warnings
warnings.filterwarnings("ignore")

def main():
    try:
        root = tk.Tk()
        app = ChatBotGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")

if __name__ == "__main__":
    main()