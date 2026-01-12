import argparse
from pathlib import Path
from dotenv import load_dotenv
from server.server import Server

load_dotenv()

def get_config_path() -> str:
    """Get config path from CLI args or use default."""
    parser = argparse.ArgumentParser(description="Inference API Server")
    parser.add_argument(
        "--config",
        "-c",
        type=str,
        default="server/config.yaml",
        help="Path to config.yaml file (default: server/config.yaml)"
    )
    
    args, _ = parser.parse_known_args()
    return args.config


config_path = get_config_path()

if not Path(config_path).exists():
    print(f"⚠️  Warning: Config file not found at {config_path}")
    print(f"   Using default: server/config.yaml")
    config_path = "server/config.yaml"

server = Server(config_path=config_path)

app = server.app