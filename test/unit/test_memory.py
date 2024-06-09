import json
import os
from tempfile import TemporaryDirectory

import pytest

from src.llm_agent_gui import memory


class TestSummaryBufferMemory:

    @pytest.fixture
    def summary_buffer(self) -> memory.SummaryBufferMemory:
        return memory.SummaryBufferMemory(5, "test_character")

    def test_has_empty_buffer_history(
        self, summary_buffer: memory.SummaryBufferMemory, monkeypatch
    ):
        with TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(
                summary_buffer,
                "_SUMMARY_BUFFER_PATH",
                os.path.join(tmpdir, "{}.json"),
            )

            assert summary_buffer.has_empty_buffer_history()

            with open(os.path.join(tmpdir, "test_character.json"), "w") as f:
                f.write('["", [{"message": "some message"}]]')

            assert not summary_buffer.has_empty_buffer_history()

    def test_create_character_file_if_missing(
        self, summary_buffer: memory.SummaryBufferMemory, monkeypatch
    ):
        with TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(
                summary_buffer,
                "_SUMMARY_BUFFER_PATH",
                os.path.join(tmpdir, "{}.json"),
            )

            summary_buffer.create_character_file_if_missing()

            with open(os.path.join(tmpdir, "test_character.json"), "r") as f:
                data = json.load(f)
                assert data == ["", []]

    def test_reset_character_session_on_disk(
        self, summary_buffer: memory.SummaryBufferMemory, monkeypatch
    ):
        with TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(
                summary_buffer,
                "_SUMMARY_BUFFER_PATH",
                os.path.join(tmpdir, "{}.json"),
            )

            summary_buffer.reset_character_session_on_disk()

            with open(os.path.join(tmpdir, "test_character.json"), "r") as f:
                data = json.load(f)
                assert data == ["", []]

    def test_save_new_summary_on_disk(
        self, summary_buffer: memory.SummaryBufferMemory, monkeypatch
    ):
        with TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(
                summary_buffer,
                "_SUMMARY_BUFFER_PATH",
                os.path.join(tmpdir, "{}.json"),
            )

            with open(os.path.join(tmpdir, "test_character.json"), "w") as f:
                f.write('["old summary", [{"message": "some message"}]]')

            summary_buffer.save_new_summary_on_disk("new summary")

            with open(os.path.join(tmpdir, "test_character.json"), "r") as f:
                data = json.load(f)
                assert data == ["new summary", [{"message": "some message"}]]

    def test_save_initial_buffer_on_disk(
        self, summary_buffer: memory.SummaryBufferMemory, monkeypatch
    ):
        with TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(
                summary_buffer,
                "_SUMMARY_BUFFER_PATH",
                os.path.join(tmpdir, "{}.json"),
            )

            summary_buffer.save_initial_buffer_on_disk([{"message": "test"}])

            with open(os.path.join(tmpdir, "test_character.json"), "r") as f:
                data = json.load(f)
                assert data == ["", [{"message": "test"}]]

    def test_expand_buffer_on_disk(
        self, summary_buffer: memory.SummaryBufferMemory, monkeypatch
    ):
        with TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(
                summary_buffer,
                "_SUMMARY_BUFFER_PATH",
                os.path.join(tmpdir, "{}.json"),
            )
            with open(os.path.join(tmpdir, "test_character.json"), "w") as f:
                f.write('["some summary", [{"message": "old"}]]')

            summary_buffer.expand_buffer_on_disk([{"message": "new"}])

            with open(os.path.join(tmpdir, "test_character.json"), "r") as f:
                data = json.load(f)
                assert data == [
                    "some summary",
                    [{"message": "old"}, {"message": "new"}],
                ]

    def test_load_summary_from_disk(
        self, summary_buffer: memory.SummaryBufferMemory, monkeypatch
    ):
        with TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(
                summary_buffer,
                "_SUMMARY_BUFFER_PATH",
                os.path.join(tmpdir, "{}.json"),
            )
            with open(os.path.join(tmpdir, "test_character.json"), "w") as f:
                f.write('["test summary", [{"message": "some message"}]]')

            assert summary_buffer.load_summary_from_disk() == "test summary"

    def test_load_buffer_from_disk(
        self, summary_buffer: memory.SummaryBufferMemory, monkeypatch
    ):
        with TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(
                summary_buffer,
                "_SUMMARY_BUFFER_PATH",
                os.path.join(tmpdir, "{}.json"),
            )
            with open(os.path.join(tmpdir, "test_character.json"), "w") as f:
                f.write('["some summary", [{"message": "test"}]]')

            assert summary_buffer.load_buffer_from_disk() == [{"message": "test"}]

    def test_reset_buffer_on_disk(
        self, summary_buffer: memory.SummaryBufferMemory, monkeypatch
    ):
        with TemporaryDirectory() as tmpdir:
            monkeypatch.setattr(
                summary_buffer,
                "_SUMMARY_BUFFER_PATH",
                os.path.join(tmpdir, "{}.json"),
            )
            with open(os.path.join(tmpdir, "test_character.json"), "w") as f:
                f.write('["some summary", [{"message": "test"}]]')

            summary_buffer.reset_buffer_on_disk()

            with open(os.path.join(tmpdir, "test_character.json"), "r") as f:
                data = json.load(f)
                assert data == ["some summary", []]


class TestVectorStore:

    @pytest.fixture
    def vector_store(self) -> memory.VectorStoreMemory:
        vector_store_instance = memory.VectorStoreMemory(
            2, "test_character", vector_store_path="test/temp"
        )
        vector_store_instance.chroma_client.delete_collection("test_character")
        return vector_store_instance

    @pytest.fixture
    def setup(self, vector_store: memory.VectorStoreMemory):
        vector_store.collection = vector_store.chroma_client.get_or_create_collection(
            "test_character"
        )
        yield
        vector_store.chroma_client.delete_collection("test_character")

    def test_set_session(self, vector_store: memory.VectorStoreMemory):
        character_name = "test_character"
        vector_store.set_session(character_name)
        assert character_name == vector_store.collection.name
        vector_store.chroma_client.delete_collection("test_character")

    def test_save_new_lines_as_vectors(
        self, vector_store: memory.VectorStoreMemory, setup
    ):
        new_lines = [
            {"role": "user", "content": "Hello there"},
            {"role": "assistant", "content": "General Kenobi"},
        ]
        character_name = "test_character"
        vector_store.save_new_lines_as_vectors(new_lines, character_name)
        assert vector_store.collection.count() == len(new_lines)

    def test_retreive_related_information(
        self, vector_store: memory.VectorStoreMemory, setup
    ):
        new_lines = [
            {"role": "user", "content": "Hello there"},
            {"role": "assistant", "content": "General Kenobi"},
        ]
        vector_store.save_new_lines_as_vectors(new_lines, "test_character")

        # Retrieve related information
        chatbot_answer = "Kenobi"
        results = vector_store.retreive_related_information(chatbot_answer)

        # Assert that the returned documents match expected output
        assert "test_character: General Kenobi" in results

    def test_create_string_ids(self, vector_store: memory.VectorStoreMemory, setup):
        new_lines = [
            {"role": "user", "content": "Hello there"},
            {"role": "assistant", "content": "General Kenobi"},
        ]
        vector_store.save_new_lines_as_vectors(new_lines, "test_character")

        string_ids = vector_store.create_string_ids(4)
        assert string_ids == ["id2", "id3", "id4", "id5"]

    def test_reset_colletion(self, vector_store: memory.VectorStoreMemory, setup):
        new_lines = [
            {"role": "user", "content": "Hello there"},
            {"role": "assistant", "content": "General Kenobi"},
        ]
        vector_store.save_new_lines_as_vectors(new_lines, "test_character")

        vector_store.reset_collection("test_character")

        assert vector_store.collection.count() == 0

    def test_get_full_chat_history(
        self, vector_store: memory.VectorStoreMemory, setup, user_name: str
    ):
        new_lines = [
            {"role": "user", "content": "Hello there"},
            {"role": "assistant", "content": "General Kenobi"},
            {"role": "user", "content": "General who?"},
            {"role": "assistant", "content": "Exactly."},
        ]
        vector_store.save_new_lines_as_vectors(new_lines, "test_character")

        chat_history = vector_store.get_full_chat_history()

        assert (
            chat_history
            == user_name
            + ": hello there\n\nTest_character: general kenobi\n\n"
            + user_name
            + ": general who?\n\nTest_character: exactly.\n\n"
        )
