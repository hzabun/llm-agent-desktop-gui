from typing import Any

from llama_cpp import Llama
from openai import OpenAI
from transformers import pipeline


class LlmBackend:
    def __init__(self, backend: str):
        self.classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            return_all_scores=True,
        )
        if backend == "llama-cpp":
            self.initialize_llama_cpp()
        elif backend == "openai":
            self.initialize_openai()
        else:
            raise Exception("No valid backend option passed!")

    def initialize_llama_cpp(self):
        self.llama_cpp_llm = Llama(
            model_path="src/llm_agent_gui/llm_weights/openhermes-2.5-mistral-7b.Q5_K_M.gguf",
            n_ctx=4096,
            chat_format="chatml",
            verbose=False,
            n_gpu_layers=-1,  # load all layers to GPU
        )

        self.inference_llm = self.inference_llama_cpp

    def initialize_openai(self):
        self.openai_llm = OpenAI()
        self.inference_llm = self.inference_openai

    def inference_openai(
        self, prompt: list[Any]
    ) -> str:  # TODO: find proper way to hint types
        completion = self.openai_llm.chat.completions.create(
            model="gpt-3.5-turbo", messages=prompt
        )

        return completion.choices[0].message.content  # type: ignore

    def inference_llama_cpp(
        self, prompt: list[Any]
    ) -> str:  # TODO: find proper way to hint types
        output = self.llama_cpp_llm.create_chat_completion(
            messages=prompt,
            max_tokens=None,
            stop=["<|end_of_turn|>"],
            temperature=0.4,
            stream=False,
        )
        return output["choices"][0]["message"]["content"]  # type: ignore

    def classify_sentiment(self, character_response: str):
        emotion_scores = self.classifier(character_response)[0]  # type: ignore

        max_emotion = max(emotion_scores, key=lambda x: x["score"])  # type: ignore

        return max_emotion["label"]
