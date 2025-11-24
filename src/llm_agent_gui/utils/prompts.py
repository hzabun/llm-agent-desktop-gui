from typing import Any

_INITIAL_SYSTEM_PROMPT = "You are roleplaying as the character {character_name} from the {platform_type} {platform_name}. The name of the user you are talking to is {user_name}. Only talk as {character_name} and respond to {user_name}. Always stay in character and never do something {character_name} wouldn't do. React and respond the way {character_name} would react and respond. Start the conversation with something {character_name} does regularly."


def prepare_initial_system_prompt(character, user_name: str) -> str:
    prompt = _INITIAL_SYSTEM_PROMPT.format(
        character_name=character.name,
        platform_type=character.platform_type,
        platform_name=character.platform_name,
        user_name=user_name,
    )
    return prompt


_SUMMARIZER_SYSTEM_TEMPLATE = "Progressively summarize the new lines of conversation. Use the provided current summary and the new lines of conversation to create an updated summary.\n"

_SUMMARIZER_USER_TEMPLATE = """Current summary:
{current_summary}

New lines of conversation:
{new_lines}

Updated summary:"""


def prepare_summarizer_prompt(
    current_summary: str,
    new_messages: list[dict[str, str]],
    character_name: str,
    user_name: str,
) -> list[dict[str, str]]:
    new_messages_formatted = ""

    for message in new_messages:
        if message["role"] == "system":  # TODO: check if this line is still necessary
            continue
        elif message["role"] == "assistant":
            new_messages_formatted += character_name + ": " + message["content"] + "\n"
        elif message["role"] == "user":
            new_messages_formatted += user_name + ": " + message["content"] + "\n"
        else:
            new_messages_formatted += message["role"] + ": " + message["content"] + "\n"

    summary_prompt = [
        {"role": "system", "content": _SUMMARIZER_SYSTEM_TEMPLATE},
        {
            "role": "user",
            "content": _SUMMARIZER_USER_TEMPLATE.format(
                current_summary=current_summary, new_lines=new_messages_formatted
            ),
        },
    ]

    return summary_prompt


_SYSTEM_CHAT_TEMPLATE = """You are roleplaying as the character {character_name} from the {platform_type} {platform_name}. Use the following information to continue the roleplay conversation between you and the user.

Roleplay instruction rules:
{roleplay_instructions}

Use the following summary of the conversation so far as context:
{current_summary}

Additionally, use the following related messages as context:
{related_information}
"""


def prepare_system_chat_prompt(
    character,
    system_message: str,
    current_summary: str,
    context_sentences: str | list[Any],
) -> str:
    context_sentences_formatted = ""

    for sentence in context_sentences:
        context_sentences_formatted += sentence + "\n"

    return _SYSTEM_CHAT_TEMPLATE.format(
        roleplay_instructions=system_message,
        current_summary=current_summary,
        related_information=context_sentences_formatted,
        character_name=character.name,
        platform_type=character.platform_type,
        platform_name=character.platform_name,
    )


_GAME_START_PROMPT = """The user wants to play the game {game} with you and started a session right now. Do not draw the board visually, keep everything in plain text. You will make the first move in the game. For that, use the following rules to play the game with him:

Roleplay instruction rules:
{roleplay_instructions}

Summary of your conversation with {user_name} so far:
{current_summary}

Use the following function as tools to properly play the game:
{available_tools}

Here are your previous actions so far:
{action_log}
"""

_TIC_TAC_TOE_TOOLS = """Make move: Use this tool to automatically make a move.
Check board: Use this tool to anaylze the board and check if you or the user can win the game with the next round.
Respond to user: Use this tool to tell the user something. You can express your thought about the game or taunt the user to distract them from making the best move.

Start a loop and always use the following format:

Thought: you should always think about what to do
Action: the action to take, should be one of [Make move, Check board, Respond to user]
Action Input: the input to the action you take, only applicable for action 'Respond to user'

Do NOT deviate from the shown format and make sure to always include 'Thought' in your responses."""


def prepare_game_start_prompt(
    user_name: str,
    game: str,
    roleplay_instructions: str,
    current_summary: str,
    action_log: str,
) -> str:
    # if game == "Tic-Tac-Toe":
    #     game_start_prompt = _GAME_START_PROMPT.format(
    #         user_name=user_name,
    #         game=game,
    #         roleplay_instructions=roleplay_instructions,
    #         available_tools=_TIC_TAC_TOE_TOOLS,
    #     )
    #     return game_start_prompt
    # elif game == "Battleships":

    if not action_log:
        action_log = "You have not taken any action yet."

    game_start_prompt = _GAME_START_PROMPT.format(
        user_name=user_name,
        game=game,
        roleplay_instructions=roleplay_instructions,
        current_summary=current_summary,
        available_tools=_TIC_TAC_TOE_TOOLS,
        action_log=action_log,
    )
    return game_start_prompt


_GAME_CONTINUATION_PROMPT = """
Continue playing the game {game} with {user_name}. So far, you have won {ai_wins} times and {user_name} has won {user_wins} times. Do not draw the game visually. Use the following rules to properly continue playing the game with him:

Roleplay instruction rules:
{roleplay_instructions}

Summary of your conversation with {user_name} so far:
{current_summary}

Use the following functions as tools to properly continue playing the game:
{available_tools}

Here are your previous actions so far:
{action_log}
"""


def prepare_game_continue_prompt(
    user_name: str,
    game: str,
    roleplay_instructions: str,
    current_summary: str,
    ai_wins: int,
    user_wins: int,
    action_log: str,
) -> str:
    game_continue_prompt = _GAME_CONTINUATION_PROMPT.format(
        user_name=user_name,
        game=game,
        roleplay_instructions=roleplay_instructions,
        current_summary=current_summary,
        available_tools=_TIC_TAC_TOE_TOOLS,
        ai_wins=ai_wins,
        user_wins=user_wins,
        action_log=action_log,
    )
    return game_continue_prompt


_GAME_QUIT_PROMPT = """You are roleplaying as the character {character_name} from the {platform_type} {platform_name}. You were playing the game {game} with the user. The game session ended now. Use the following information to continue the roleplay conversation between you and the user.

Roleplay instruction rules:
{roleplay_instructions}

{game} game session results:
You won {ai_wins} times.
The user won {user_wins} times.

Use the following summary of the conversation so far as context:
{current_summary}

"""


def prepare_game_quit_prompt(
    character,
    game: str,
    ai_wins: int,
    user_wins: int,
    system_message: str,
    current_summary: str,
) -> str:
    return _GAME_QUIT_PROMPT.format(
        character_name=character.name,
        platform_type=character.platform_type,
        platform_name=character.platform_name,
        game=game,
        ai_wins=ai_wins,
        user_wins=user_wins,
        roleplay_instructions=system_message,
        current_summary=current_summary,
    )
