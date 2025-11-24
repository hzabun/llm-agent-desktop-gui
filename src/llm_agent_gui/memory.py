import json
import os

import chromadb

from src.llm_agent_gui.utils import format_messages


class SummaryBufferMemory:
    def __init__(self, buffer_size: int, character_name: str) -> None:
        self._buffer_size = buffer_size
        self._buffer_counter = 0
        self.character_session = character_name
        self.summary_pending = False

        self._SUMMARY_BUFFER_DIRECTORY = (
            "src/llm_agent_gui/history_logs/summary_buffer/"
        )
        self._SUMMARY_BUFFER_PATH = (
            "src/llm_agent_gui/history_logs/summary_buffer/{}.json"
        )

        try:
            os.makedirs(self._SUMMARY_BUFFER_DIRECTORY)
        except FileExistsError:
            pass

    def has_empty_buffer_history(self) -> bool:
        try:
            open(
                self._SUMMARY_BUFFER_PATH.format(self.character_session),
            )

        except FileNotFoundError:
            return True

        else:
            if self.load_buffer_from_disk():
                return False
            else:
                return True

    def create_character_file_if_missing(self) -> None:
        try:
            f = open(
                self._SUMMARY_BUFFER_PATH.format(self.character_session),
            )

        except FileNotFoundError:
            with open(
                self._SUMMARY_BUFFER_PATH.format(self.character_session),
                "w",
            ) as f:
                json.dump(["", []], f, indent=4)

    def reset_character_session_on_disk(self) -> None:
        with open(
            self._SUMMARY_BUFFER_PATH.format(self.character_session),
            "w",
        ) as f:
            json.dump(["", []], f, indent=4)

    def save_new_summary_on_disk(self, new_summary: str | None) -> None:
        with open(
            self._SUMMARY_BUFFER_PATH.format(self.character_session),
            "r+",
        ) as f:
            summary_buffer_logs = json.load(f)
            summary_buffer_logs[0] = new_summary
            f.seek(0)
            f.truncate()
            json.dump(summary_buffer_logs, f, indent=4)

    def save_initial_buffer_on_disk(self, character_greeting: dict[str, str]) -> None:
        with open(
            self._SUMMARY_BUFFER_PATH.format(self.character_session),
            "w",
        ) as f:
            new_lines_formatted = ["", [character_greeting]]
            json.dump(new_lines_formatted, f, indent=4)

    def expand_buffer_on_disk(self, new_lines: list[dict[str, str]]) -> None:
        with open(
            self._SUMMARY_BUFFER_PATH.format(self.character_session),
            "r+",
        ) as f:
            summary_buffer_logs = json.load(f)
            summary_buffer_logs[1] += new_lines
            f.seek(0)
            f.truncate()
            json.dump(summary_buffer_logs, f, indent=4)

    def load_summary_from_disk(self) -> str:
        with open(
            self._SUMMARY_BUFFER_PATH.format(self.character_session),
        ) as f:
            summary_buffer_logs = json.load(f)
            latest_summary = summary_buffer_logs[0]

        if not latest_summary:
            latest_summary = "You have no conversation summary with the user yet."
        return latest_summary

    def load_buffer_from_disk(self) -> list[dict[str, str]]:
        with open(
            self._SUMMARY_BUFFER_PATH.format(self.character_session),
        ) as f:
            summary_buffer_logs = json.load(f)
            last_messages = summary_buffer_logs[1]

            return last_messages

    def reset_buffer_on_disk(self) -> None:
        with open(
            self._SUMMARY_BUFFER_PATH.format(self.character_session),
            "r+",
        ) as f:
            summary_buffer_logs = json.load(f)
            summary_buffer_logs[1] = []
            f.seek(0)
            f.truncate()
            json.dump(summary_buffer_logs, f, indent=4)

    def update_buffer_counter(self) -> None:
        self._buffer_counter = len(self.load_buffer_from_disk())
        self.summary_pending = not (
            self._buffer_counter < self._buffer_size
        )  # parentheses for better readability, otherwise not needed due to operator precedence


class VectorStoreMemory:
    def __init__(
        self,
        num_query_results: int,
        character_name: str,
        vector_store_path: str | None = None,
    ):
        self._VECTOR_STORE_PATH = vector_store_path or (
            "src/llm_agent_gui/history_logs/vectore_store"
        )
        self.chroma_client = chromadb.PersistentClient(path=self._VECTOR_STORE_PATH)
        self.num_query_results = num_query_results
        self.set_session(character_name=character_name)

    def set_session(self, character_name: str) -> None:
        character_name_formatted = character_name.replace(" ", "_")
        self.collection = self.chroma_client.get_or_create_collection(
            name=character_name_formatted
        )

    def save_initial_lines_as_vectors(
        self, character_greeting: dict[str, str], character_name: str
    ) -> None:
        role_and_content_formatted = format_messages.format_vector_store_messages(
            character_greeting=character_greeting, character_name=character_name
        )
        str_ids = self.create_string_ids(1)
        self.collection.add(documents=role_and_content_formatted, ids=str_ids)

    def save_new_lines_as_vectors(
        self, new_lines: list[dict[str, str]], character_name: str, user_name: str
    ) -> None:
        roles_and_contents_formatted = (
            format_messages.format_multiple_vector_store_messages(
                message_lines=new_lines,
                character_name=character_name,
                user_name=user_name,
            )
        )
        str_ids = self.create_string_ids(len(roles_and_contents_formatted))
        self.collection.add(documents=roles_and_contents_formatted, ids=str_ids)

    def retreive_related_information(self, user_message: str) -> list[str]:
        results = self.collection.query(
            query_texts=user_message,
            n_results=self.num_query_results,
        )

        return results["documents"][0]  # type: ignore

    def create_string_ids(self, doc_count: int) -> list[str]:
        current_id_count = self.collection.count()
        int_ids = list(range(current_id_count, current_id_count + doc_count))
        str_ids = list(map(lambda x: "id" + str(x), int_ids))

        return str_ids

    def reset_collection(self, character_session: str) -> None:
        if character_session in [c.name for c in self.chroma_client.list_collections()]:
            message_ids = self.collection.get()["ids"]
            self.collection.delete(message_ids)
        formatted_character_name = character_session.replace(" ", "_")
        self.collection = self.chroma_client.get_or_create_collection(
            name=formatted_character_name
        )

    def get_full_chat_history(self) -> str:
        chat_messages = self.collection.get()["documents"]
        chat_history_str = ""
        if chat_messages:
            for line in chat_messages:
                chat_history_str += line.capitalize() + "\n\n"

        return chat_history_str
