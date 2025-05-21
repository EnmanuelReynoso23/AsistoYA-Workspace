import os
import webbrowser

def main():
    html_path = os.path.abspath("index.html")
    webbrowser.open(f"file://{html_path}")

if __name__ == "__main__":
    main()