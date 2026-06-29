from src.ui import build_app

app = build_app()

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860)