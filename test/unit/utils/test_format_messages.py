from src.llm_agent_gui.utils import format_messages


def test_assign_multiple_roles_to_messages():
    roles = ["user", "assistant"]
    messages = ["What a beautiful day", "But it's storming outside"]

    expected_result = [
        {"role": "user", "content": "What a beautiful day"},
        {"role": "assistant", "content": "But it's storming outside"},
    ]

    result = format_messages.assign_multiple_roles_to_messages(
        roles=roles, messages=messages
    )

    assert result == expected_result


def test_format_messages():
    new_lines = [
        {"role": "user", "content": "Hello there"},
        {"role": "assistant", "content": "General Kenobi"},
    ]
    formatted_lines = format_messages.format_multiple_vector_store_messages(
        message_lines=new_lines, character_name="test_character"
    )
    assert "test_character: General Kenobi" in formatted_lines
