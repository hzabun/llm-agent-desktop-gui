def assign_role_to_message(role: str, message: str) -> dict[str, str]:
    return {"role": role, "content": message}


def assign_multiple_roles_to_messages(
    roles: list[str], messages: list[str]
) -> list[dict[str, str]]:
    formatted_messages = [
        {"role": role, "content": message} for role, message in zip(roles, messages)
    ]

    return formatted_messages


def format_vector_store_messages(
    character_greeting: dict[str, str], character_name: str
) -> str:
    role_and_content = character_name + ": " + character_greeting["content"]

    return role_and_content


def format_multiple_vector_store_messages(
    message_lines: list[dict[str, str]], character_name: str, user_name: str
) -> list[str]:
    roles_and_contents = [
        (
            character_name + ": " + message["content"]
            if message["role"] == "assistant"
            else user_name + ": " + message["content"]
        )
        for message in message_lines
    ]

    return roles_and_contents
