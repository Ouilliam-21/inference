from server.main import Server
from dotenv import load_dotenv

load_dotenv()

server = Server()

app = server.app