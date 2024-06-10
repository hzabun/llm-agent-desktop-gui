import re
from typing import Any

from src.llm_agent_gui import llm_backend, memory
from src.llm_agent_gui.utils import character_sessions, format_messages, prompts


class Agent:

    def __init__(self, character_name: str) -> None:
        self.character = Character(character_name=character_name)
        self.name_of_user = "Halil"  # Add any name you want to be called as
        self.set_initial_system_message()

        self.summary_buffer_memory = memory.SummaryBufferMemory(
            buffer_size=10,
            character_name=self.character.name,
        )
        self.update_is_new_chat_variable()

        self.vector_store_memory = memory.VectorStoreMemory(
            num_query_results=2, character_name=self.character.name
        )
        self.llm = llm_backend.LlmBackend("openai")

        self.game_mode = False

    def set_initial_system_message(self) -> None:
        self.initial_system_message = prompts.prepare_initial_system_prompt(
            character=self.character, user_name=self.name_of_user
        )

    def update_is_new_chat_variable(self) -> None:
        self.is_new_chat = self.summary_buffer_memory.has_empty_buffer_history()

    def inference_system_message(self) -> str:
        initial_prompt = format_messages.assign_role_to_message(
            role="system",
            message=self.initial_system_message,
        )
        character_response = self.llm.inference_llm([initial_prompt])

        return character_response

    def clean_agent_response(self, response: str) -> str:
        clean_input_pattern = r"^[\s\S]*?(Thought:)"
        clean_input = re.sub(clean_input_pattern, r"\1", response)
        return clean_input

    def extract_action_and_input(self, response: str) -> tuple[list[Any], list[Any]]:
        clean_input_pattern = r"^.*?(Thought:)"
        action_pattern = r"Action: (.+?)(?:\n|$)"
        input_pattern = r"Action Input:\s*(.*)"

        clean_input = re.sub(clean_input_pattern, r"\1", response)
        action = re.findall(action_pattern, clean_input)
        action_input = re.findall(input_pattern, clean_input)
        return action, action_input

    def character_agent_response_handler(self, user_message: str) -> str:
        if self.game_mode:
            return ""
        else:
            chat_prompt = self.create_prompt(user_message=user_message)
            character_response = self.llm.inference_llm(prompt=chat_prompt)

            return character_response

    def create_prompt(self, user_message: str) -> list[dict[str, str]]:
        current_summary = self.summary_buffer_memory.load_summary_from_disk()
        last_messages = self.summary_buffer_memory.load_buffer_from_disk()
        user_message_formatted = format_messages.assign_role_to_message(
            role="user", message=user_message
        )

        if not current_summary:
            chat_prompt = last_messages + [user_message_formatted]
            return chat_prompt

        else:
            related_information = self.vector_store_memory.retreive_related_information(
                user_message=user_message
            )
            system_prompt = prompts.prepare_system_chat_prompt(
                character=self.character,
                system_message=self.initial_system_message,
                current_summary=current_summary,
                context_sentences=related_information,
            )
            system_prompt_formatted = format_messages.assign_role_to_message(
                role="system", message=system_prompt
            )
            chat_prompt = (
                [system_prompt_formatted] + last_messages + [user_message_formatted]
            )
            return chat_prompt

    def save_answer_on_disk_handler(
        self, user_message: str, character_answer: str
    ) -> None:
        if self.is_new_chat:

            character_greeting_formatted = format_messages.assign_role_to_message(
                role="assistant", message=character_answer
            )
            self.save_initial_character_answer_on_disk(
                character_greeting=character_greeting_formatted,
            )

        else:
            new_lines_to_save = format_messages.assign_multiple_roles_to_messages(
                roles=["user", "assistant"],
                messages=[user_message, character_answer],
            )
            self.save_subsequent_character_answer_on_disk(new_lines=new_lines_to_save)

    def save_initial_character_answer_on_disk(
        self,
        character_greeting: dict[str, str],
    ) -> None:

        self.summary_buffer_memory.save_initial_buffer_on_disk(
            character_greeting=character_greeting
        )
        self.summary_buffer_memory.update_buffer_counter()
        self.vector_store_memory.save_initial_lines_as_vectors(
            character_greeting=character_greeting, character_name=self.character.name
        )
        self.is_new_chat = False

    def save_subsequent_character_answer_on_disk(
        self, new_lines: list[dict[str, str]]
    ) -> None:
        self.vector_store_memory.save_new_lines_as_vectors(
            new_lines=new_lines,
            character_name=self.character.name,
            user_name=self.name_of_user,
        )

        if not self.summary_buffer_memory.summary_pending:
            self.summary_buffer_memory.expand_buffer_on_disk(new_lines=new_lines)
            self.summary_buffer_memory.update_buffer_counter()

        else:
            new_summary = self.generate_new_summary()
            self.summary_buffer_memory.save_new_summary_on_disk(new_summary=new_summary)
            self.summary_buffer_memory.reset_buffer_on_disk()
            self.summary_buffer_memory.expand_buffer_on_disk(new_lines=new_lines)
            self.summary_buffer_memory.update_buffer_counter()

    def generate_new_summary(self) -> str:
        current_summary = self.summary_buffer_memory.load_summary_from_disk()
        last_messages = self.summary_buffer_memory.load_buffer_from_disk()
        summarizer_prompt = prompts.prepare_summarizer_prompt(
            current_summary=current_summary,
            new_messages=last_messages,
            character_name=self.character.name,
            user_name=self.name_of_user,
        )
        new_summary = self.llm.inference_llm(prompt=summarizer_prompt)
        return new_summary


class Character:

    def __init__(self, character_name: str) -> None:
        self.name = character_name

        self.character_info = character_sessions.get_character_list()
        self.platform_type = self.character_info[self.name]["platform_type"]
        self.platform_name = self.character_info[self.name]["platform_name"]

    def set_character(self, character_name: str) -> None:
        self.name = character_name
        self.platform_type = self.character_info[self.name]["platform_type"]
        self.platform_name = self.character_info[self.name]["platform_name"]
