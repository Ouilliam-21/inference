import yaml
from typing import Optional, Dict, Any

class EventPrompt:
    template: str

    def __init__(self, template: str):
        self.template = template

class PromptConfig:
    system_prompt: str
    event_prompts: Optional[Dict[str, EventPrompt]] = None

    def __init__(self, system_prompt: str, event_prompts: Optional[Dict[str, EventPrompt]] = None):
        self.system_prompt = system_prompt
        self.event_prompts = event_prompts

    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'PromptConfig':
        """Load and parse YAML config file into PromptConfig object"""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

            event_prompts = {}
            for event_name, event_prompt in data["event_prompts"].items():
                event_prompts[event_name] = EventPrompt(template=event_prompt["template"])

            return PromptConfig(
                system_prompt=data["system_prompt"],
                event_prompts=event_prompts
            )
     
class PromptManager:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()

    def _load_config(self):
        """Load YAML config and convert to Python object"""
        return PromptConfig.from_yaml(self.config_path)

    def get_system_prompt(self) -> str:
        return self.config.system_prompt
    
    def get_prompt(self, event_name: str, event_data: Optional[Dict[str, Any]] = None) -> str:
        """Get prompt template, optionally with variables replaced"""
        template = self.config.event_prompts[event_name].template
        
        # Si event_data est fourni, remplacer les variables
        if event_data:
            try:
                return template.format(**event_data)
            except KeyError as e:
                raise ValueError(f"Variable manquante dans event_data: {e}")
        
        return template
if __name__ == "__main__":
    
    manager = PromptManager("config.yaml")
    
    # Exemple d'utilisation avec des données d'événement
    champion_kill_data = {
        "VictimName": "Yasuo",
        "KillerName": "Jhin"
    }
    
    prompt = manager.get_prompt("ChampionKill", champion_kill_data)
    print(prompt)