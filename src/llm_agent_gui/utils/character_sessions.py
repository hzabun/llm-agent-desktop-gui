import json

_CHARACTERS_LIST_PATH = "src/llm_agent_gui/characters.json"


def get_character_list() -> dict[str, dict[str, str]]:
    with open(
        _CHARACTERS_LIST_PATH,
        "r",
    ) as f:
        characters = json.load(f)

    return characters
