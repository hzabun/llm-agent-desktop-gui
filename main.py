from dotenv import load_dotenv

from src.llm_agent_gui import app

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    application = app.App()
    application.mainloop()
