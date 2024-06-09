# LLM agent desktop GUI
A desktop GUI to interact with an LLM agent (chatbot which can use external tools).

## Description

This project was primarily created for practice purposes. Goal was to learn how to implement an LLM agent with the ReAct framework ([original paper](https://arxiv.org/abs/2210.03629), [quick-read article](https://www.promptingguide.ai/techniques/react)), which means a chatbot which can reason what to do next and can use tools. Additionally, I wanted to learn how to apply sentiment analysis on an agents response.

Main LLMs can be run locally via [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) or via the OpenAI API (needs an access key). Sentiment analysis is done via a [fine-tuned DistilRoBERTa-base](https://huggingface.co/j-hartmann/emotion-english-distilroberta-base) model and run via the [HF tranformers](https://huggingface.co/docs/transformers/en/main_classes/pipelines) library.

### Features

- Chatbot can play a game of "Tic-Tac-Toe" with you by executing tools
- Chatbot takes the role of a specific character you can choose and acts as much as possible the way that character would act
- Specific character can be anyone from movies, video games, anime etc. (see "characters.json" for a list of characters I used)
- Image of character changes based on the characters current emotion (currently only implemented for Goku)

Tip: Gordon Freeman is my favorite chat buddy


## Installation

1. Clone the repository:
```
git clone https://github.com/hzabun/llm-agent-desktop-gui
cd llm-agent-desktop-gui
```

2. Create and activate a virtual environment
```
# For MacOS and Unix
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
.\venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Install [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)
    - Follow the custom installation instructions for your machine
    - Alternatively use an OpenAI API key by adding "openai" [here](https://github.com/hzabun/llm-agent-desktop-gui/blob/main/src/llm_agent_gui/agent.py#L24)

5. Download an LLM and save it under *src/llm_dnd_dm/llm_weights*
    - I used [Openhermes 2.5 Mistral 7B - GGUF](https://huggingface.co/TheBloke/OpenHermes-2.5-Mistral-7B-GGUF)
    - Make sure to update the path name to your LLM in **llm_backend.py** [here](https://github.com/hzabun/llm-agent-desktop-gui/blob/main/src/llm_agent_gui/llm_backend.py#L26)
    - Tip: 7B models seem to struggle a bit with following ReAct format, bigger models recommended

### Usage
Run main.py
```
python main.py
```
Engage with the character, change character if you like and play a game of Tic-Tac-Toe. All conversation is saved locally.

## Implementation details

### LLM backend
Backend is implemented with [llama-cpp-python](https://github.com/abetlen/llama-cpp-python). It supports offloading layers to CPU **and** GPU, which is very handy if your model doesn't fit your GPU memory. I'm using an M1 iMac for running the LLM locally. Also chose OpenHermes as it has overall good test results for these kinds of use cases.

Optionally, you can just use the OpenAI API.

Current LLM configuration for llama-cpp-python:
- Model: **TheBloke/OpenHermes-2.5-Mistral-7B-GGUF** (Q5_K_M quantization)
- Context window size = **4096** (number of tokens)
- Chat format: **chatml** (necessary for OpenHermes)
- Offloaded GPU layers: **-1** (all layers)

### Memory modules
There are 2 memory types implemented:
- Summary buffer memory for short to mid-term retention
- Vector store for long-term retention

Both of them saved locally on disk to be able to continue your last session after shutting down the program.

#### Summary buffer memory
A simple JSON file on disk which contains a summary of the chat history so far and an adjustable buffer with the last **n** messages. Every time you send and receive a message from the chatbot, that message is stored into the buffer. Once the buffer is full the LLM takes the summary it has so far and updates it with the new messages in the buffer. Then the buffer gets emptied, ready to be filled with new messages in your conversation with the chatbot.

#### Vector store
The vector store is implemented with [chromadb](https://github.com/chroma-core/chroma). A vector store contains a list of documents embedded as vectors, meaning each documents gets converted into a list of numbers. That allows us to first add **all** messages to our vector store as vectors. Then, whenever we send a prompt to the chatbot, it can query the vector store to search for previous messages which are similar to the prompt.

Quick example: Assume you're chatting with Gordon Freeman and at the begining you told him how it is your dream to work at the Black Mesa facility. If sometime later in your chat you talk about how frightening working at the Black Mesa facility sounds to you, Gordon might pick up on that and ask you confused if it wasn't your dream to actually work there. This way, he builds sort of a long-term memory and feels a bit more natural.

### GUI
The GUI is implemented with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter). An easy to use UI-library to create our basic chatbot GUI. It takes the user input as prompt, inferences the LLM and shows the output in a textbox. It also shows the Tic-Tac-Toe game visually with buttons to click.

## Known bugs
There are a couple known bugs in the project so far, including:
- Sometimes the LLM does not use the proper ReAct format during a Tic-Tac-Toe session, e.g. leaving out the "Thought:" part
- Sometimes the LLM gets stuck during a Tic-Tac-Toe session in an infinite loop of "Check board" action (currently catching that behaviour, but this feels like treating sympytons rather than the underlying cause)
- 

## Next steps
Aside from the known bugs, the project is considered complete the way it is right now, as it fulfills my goals of this practice project. However, I might implement further adjustments and extensions in the future.

### Expanding sentiment analysis to all characters
Currently, only Goku has this feature implemented and whenever his mood changes his images changes with it.

### Expanding sentiment analysis for Tic-Tac-Toe game
Sentiment analysis is currently only applied during normal chat sessions. When a character, say Goku, feels stressed during a Tic-Tac-Toe session it's not getting reflected in his image.

### Add more games
Simple 2D games like battleship or chess can be easily added to the game list.

### Expand tool selection
The characters could be equipped with even more tools, including Google searches, code checkers etc. to get things done while having a relaxed (or less relaxed) chat with your favorite character.