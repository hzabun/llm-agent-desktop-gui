import tkinter

import customtkinter
from PIL import Image

from src.llm_agent_gui import agent, games
from src.llm_agent_gui.utils import character_sessions

customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("blue")


class ChooseCharacterSessionWindow(customtkinter.CTkToplevel):
    def __init__(self, cancellable: bool = False) -> None:
        super().__init__()

        available_characters = list(character_sessions.get_character_list().keys())

        self._user_input: str
        self._running: bool = False
        self._title = "Choose character"
        self._text = "Choose your LLM agent buddy"

        self.title(self._title)
        self.lift()  # lift window on top
        self.attributes("-topmost", True)  # stay on top
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self._create_widgets(
            available_characters=available_characters, cancellable=cancellable
        )
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

    def _create_widgets(
        self, available_characters: list[str], cancellable: bool
    ) -> None:
        self.grid_columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(
            master=self,
            width=300,
            wraplength=300,
            text=self._text,
        )
        self.label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self.characters_session_option_menu = customtkinter.CTkOptionMenu(
            master=self, values=available_characters
        )
        self.characters_session_option_menu.grid(
            row=1, column=0, columnspan=2, padx=(35, 35), pady=(20, 20), sticky="ew"
        )

        self.ok_button = customtkinter.CTkButton(
            master=self, width=100, border_width=0, text="Ok", command=self._ok_event
        )
        self.ok_button.grid(row=2, column=0, padx=(20, 20), pady=(0, 20))

        self._user_input = self.characters_session_option_menu.get()

        if cancellable:
            self.cancel_button = customtkinter.CTkButton(
                master=self,
                width=100,
                border_width=0,
                text="Cancel",
                command=self._cancel_event,
            )
            self.cancel_button.grid(row=2, column=1, padx=(20, 20), pady=(0, 20))

    def _ok_event(self, event=None) -> None:
        self._user_input = self.characters_session_option_menu.get()
        self.grab_release()
        self.destroy()

    def _on_closing(self) -> None:
        self.grab_release()
        self.destroy()

    def _cancel_event(self) -> None:
        self._user_input = ""
        self.grab_release()
        self.destroy()

    def get_input(self) -> str:
        self.master.wait_window(self)
        return self._user_input


class App(customtkinter.CTk):
    def __init__(self) -> None:
        super().__init__()

        initial_character_session_window = ChooseCharacterSessionWindow()
        selected_character = initial_character_session_window.get_input()

        self.title(f"Conversation with {selected_character}")
        self.geometry(f"{1400}x{900}")

        self.grid_columnconfigure(0, weight=20)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=40)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.character_agent = agent.Agent(
            character_name=selected_character,
        )

        self.create_widgets()

    def create_widgets(self) -> None:
        self.chat_history = customtkinter.CTkTextbox(self)
        self.chat_history.configure(state="disabled")
        self.chat_history.grid(row=0, padx=(20, 0), pady=(20, 0), sticky="nsew")

        self.typing_game_choice_frame = TypingSummarizingGameChoiceFrame(
            master=self, fg_color="transparent"
        )
        self.typing_game_choice_frame.grid(
            row=1,
            column=0,
            padx=(20, 0),
            pady=(5, 0),
            sticky="ew",
        )

        self.user_input_entry = customtkinter.CTkEntry(
            self,
            placeholder_text=f"What do you tell {self.character_agent.character.name}?",
        )
        self.user_input_entry.grid(row=2, column=0, padx=(20, 0), sticky="ew")
        self.user_input_entry.bind("<Return>", self.user_input_prompt_handler)

        self.character_image_game_frame = CharacterImageGameFrame(
            master=self, fg_color="transparent"
        )
        self.character_image_game_frame.grid(row=0, column=1, pady=(23, 0), sticky="n")

        self.session_buttons_frame = SessionButtonsFrame(
            master=self,
            fg_color="transparent",
        )
        self.session_buttons_frame.grid(row=2, column=1)

        if self.character_agent.is_new_chat:
            self.initialize_character_greeting()
        else:
            self.restore_chat_history()

    def initialize_character_greeting(self) -> None:
        self.chat_history.configure(state="normal")
        self.typing_game_choice_frame.is_typing_label.configure(text_color="black")
        self.update()
        character_response = self.character_agent.inference_system_message()
        self.chat_history.insert(
            customtkinter.END,
            self.character_agent.character.name + ": " + character_response + "\n\n",
        )
        self.typing_game_choice_frame.is_typing_label.configure(
            text_color=self.cget("bg")
        )
        self.update()
        self.chat_history.configure(state="disabled")

        self.update_character_agent_memory(prompt="", agent_answer=character_response)

    # TODO: entry bind sends pressed key event as argument, proper catching of argument necessary in method
    def user_input_prompt_handler(self, event=None) -> None:
        prompt = self.user_input_entry.get()
        self.user_input_entry.delete(0, customtkinter.END)
        self.chat_history.configure(state="normal")
        self.chat_history.insert(
            customtkinter.END,
            self.character_agent.name_of_user + ": " + prompt + "\n\n",
        )
        self.chat_history.configure(state="disabled")
        self.typing_game_choice_frame.is_typing_label.configure(text_color="black")
        self.update()

        character_response = self.character_agent.character_agent_response_handler(
            user_message=prompt
        )
        current_character_emotion = self.character_agent.llm.classify_sentiment(
            character_response=character_response
        )

        self.character_image_game_frame.change_character_image(
            new_character=self.character_agent.character.name,
            emotion=current_character_emotion,
        )

        self.add_agent_answer_to_chat_history(character_response=character_response)

        self.update_character_agent_memory(
            prompt=prompt, agent_answer=character_response
        )

    def add_agent_answer_to_chat_history(self, character_response: str):
        self.chat_history.configure(state="normal")
        self.chat_history.insert(
            customtkinter.END,
            self.character_agent.character.name + ": " + character_response + "\n\n",
        )
        self.chat_history.configure(state="disabled")
        self.typing_game_choice_frame.is_typing_label.configure(
            text_color=self.cget("bg")
        )
        self.update()

    def update_character_agent_memory(self, prompt: str, agent_answer: str) -> None:
        if self.character_agent.summary_buffer_memory.summary_pending:
            self.typing_game_choice_frame.summarizing_label.grid()
            self.update()
            self.character_agent.save_answer_on_disk_handler(
                user_message=prompt, character_answer=agent_answer
            )
            self.typing_game_choice_frame.summarizing_label.grid_remove()
            self.update()

        else:
            self.character_agent.save_answer_on_disk_handler(
                user_message=prompt, character_answer=agent_answer
            )

    def clear_chat_history(self) -> None:
        self.chat_history.configure(state="normal")
        self.chat_history.delete("0.0", customtkinter.END)
        self.chat_history.configure(state="disabled")

    def restore_chat_history(self) -> None:
        self.chat_history.configure(state="normal")
        self.chat_history.delete("0.0", customtkinter.END)
        self.chat_history.insert(
            "0.0", self.character_agent.vector_store_memory.get_full_chat_history()
        )
        self.chat_history.configure(state="disabled")

    def reset_game(self):
        self.actions_taken = []


class CharacterImageGameFrame(customtkinter.CTkFrame):
    def __init__(self, master: App, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.main_app = master

        emotion_list = [
            "neutral",
            "joy",
            "fear",
            "anger",
            "disgust",
            "surprise",
            "sadness",
        ]

        self.goku_emotion_images = {
            "goku_" + emotion: customtkinter.CTkImage(
                light_image=Image.open(
                    fp="src/llm_agent_gui/images/goku/goku_" + emotion + ".png"
                ),
                size=(300, 300),
            )
            for emotion in emotion_list
        }

        self.character_images = {
            character: customtkinter.CTkImage(
                light_image=Image.open(
                    fp=f"src/llm_agent_gui/images/{character.lower().replace(' ', '_')}/{character.lower().replace(' ', '_')}_neutral.png"
                ),
                size=(300, 300),
            )
            for character in list(character_sessions.get_character_list().keys())
        }

        self.create_widgets()

    def create_widgets(self):
        self.character_label_image = customtkinter.CTkLabel(
            self,
            image=self.character_images[self.main_app.character_agent.character.name],
            text="",
        )  # display image with a CTkLabel
        self.character_label_image.grid(row=0, column=0)

        self.tic_tac_toe = games.TicTacToe(master=self, main_app=self.main_app)
        self.tic_tac_toe.grid(row=1, column=0, pady=(20, 0))
        self.tic_tac_toe.grid_remove()

    def change_character_image(self, new_character: str, emotion: str):
        new_character = new_character.lower()
        if new_character == "goku":
            self.character_label_image.configure(
                image=self.goku_emotion_images[new_character + "_" + emotion]
            )

        else:
            self.character_label_image.configure(
                image=self.character_images[new_character]
            )


class SessionButtonsFrame(customtkinter.CTkFrame):
    def __init__(self, master: App, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.main_app = master
        self.create_widgets()

    def create_widgets(self) -> None:
        self.change_character_image = customtkinter.CTkImage(
            light_image=Image.open(
                fp="src/llm_agent_gui/images/buttons/change_character.png"
            ),
            size=(25, 25),
        )
        self.send_user_input_button = customtkinter.CTkButton(
            self, text="Send", command=self.main_app.user_input_prompt_handler
        )
        self.send_user_input_button.grid(row=0, column=0, padx=(0, 10))

        self.change_character_button = customtkinter.CTkButton(
            self,
            command=self.change_character_handler,
            image=self.change_character_image,
            text="",
            fg_color="transparent",
            hover=False,
            width=25,
            height=25,
        )
        self.change_character_button.grid(row=0, column=1, padx=5, pady=(5, 5))

        self.reset_button_image = customtkinter.CTkImage(
            light_image=Image.open(
                fp="src/llm_agent_gui/images/buttons/reset_conversation.png"
            ),
            size=(25, 25),
        )
        self.reset_session_button = customtkinter.CTkButton(
            self,
            command=self.reset_session,
            image=self.reset_button_image,
            text="",
            fg_color="transparent",
            hover=False,
            width=25,
            height=25,
        )
        self.reset_session_button.grid(
            row=0,
            column=2,
        )
        Tooltip(self.change_character_button, "Change character")
        Tooltip(self.reset_session_button, "Reset conversation")

    def change_character_handler(self) -> None:
        character_window = ChooseCharacterSessionWindow(cancellable=True)
        selected_character = character_window.get_input()

        if selected_character:
            self.set_character_session(character_name=selected_character)
            self.main_app.title(f"Conversation with {selected_character}")
            self.main_app.character_image_game_frame.character_label_image.configure(
                image=self.main_app.character_image_game_frame.character_images[
                    selected_character
                ]
            )
            self.main_app.typing_game_choice_frame.is_typing_label.configure(
                text=f"{selected_character} is typing..."
            )
            if self.main_app.character_agent.is_new_chat:
                self.main_app.clear_chat_history()
                self.main_app.initialize_character_greeting()
            else:
                self.main_app.restore_chat_history()

    def set_character_session(self, character_name: str) -> None:
        self.main_app.character_agent.character.set_character(
            character_name=character_name
        )
        self.main_app.character_agent.set_initial_system_message()
        self.main_app.character_agent.summary_buffer_memory.character_session = (
            character_name
        )
        self.main_app.character_agent.update_is_new_chat_variable()
        self.main_app.character_agent.summary_buffer_memory.create_character_file_if_missing()
        self.main_app.character_agent.summary_buffer_memory.update_buffer_counter()
        self.main_app.character_agent.vector_store_memory.set_session(
            character_name=character_name
        )

    def reset_session(self) -> None:
        reset_session_window = ResetConversationWindow()
        session_reset_confirmed = reset_session_window.get_input()
        if session_reset_confirmed:
            self.main_app.clear_chat_history()
            self.main_app.character_agent.summary_buffer_memory.reset_character_session_on_disk()
            self.main_app.character_agent.vector_store_memory.reset_collection(
                self.main_app.character_agent.character.name
            )
            self.main_app.character_agent.summary_buffer_memory.update_buffer_counter()
            self.main_app.character_agent.is_new_chat = True
            self.main_app.initialize_character_greeting()


class TypingSummarizingGameChoiceFrame(customtkinter.CTkFrame):
    def __init__(self, master: App, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.main_app = master
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.create_widgets()

    def create_widgets(self) -> None:
        self.is_typing_label = customtkinter.CTkLabel(
            self,
            text=f"{self.main_app.character_agent.character.name} is typing...",
            wraplength=200,
        )
        self.is_typing_label.grid(row=0, column=0, padx=(20, 20), sticky="w")
        self.is_typing_label.configure(text_color=self.main_app.cget("bg"))

        self.summarizing_label = customtkinter.CTkLabel(
            self,
            text="Summarizing chat history...",
            wraplength=200,
            text_color="red",
        )
        self.summarizing_label.grid(row=0, column=1)
        self.summarizing_label.grid_remove()

        self.game_select_button = customtkinter.CTkButton(
            self, text="Choose game", command=self.select_game
        )
        self.game_select_button.grid(row=0, column=2, padx=(0, 10), sticky="e")

    def select_game(self):
        choose_game_window = ChooseGameWindow(main_app=self.main_app)
        chosen_game = choose_game_window.get_input()
        if chosen_game == "Tic-Tac-Toe":
            self.main_app.character_image_game_frame.tic_tac_toe.grid()
            self.main_app.character_image_game_frame.tic_tac_toe.play_game()


class ChooseGameWindow(customtkinter.CTkToplevel):
    def __init__(self, main_app: App) -> None:
        super().__init__()

        self._user_input: str
        self._running: bool = False
        self._title = "Choose a game"
        self._text = f"Which game do you want to play with {main_app.character_agent.character.name}?"

        self.title(self._title)
        self.lift()  # lift window on top
        self.attributes("-topmost", True)  # stay on top
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self._create_widgets()
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

    def _create_widgets(self) -> None:
        self.grid_columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(
            master=self,
            width=300,
            wraplength=300,
            text=self._text,
        )
        self.label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self.game_list_option_menu = customtkinter.CTkOptionMenu(
            master=self, values=["Tic-Tac-Toe"]
        )
        self.game_list_option_menu.grid(
            row=1, column=0, columnspan=2, padx=(35, 35), pady=(20, 20), sticky="ew"
        )

        self.ok_button = customtkinter.CTkButton(
            master=self, width=100, border_width=0, text="Ok", command=self._ok_event
        )
        self.ok_button.grid(row=2, column=0, padx=(20, 20), pady=(0, 20))

        self._user_input = self.game_list_option_menu.get()

        self.cancel_button = customtkinter.CTkButton(
            master=self,
            width=100,
            border_width=0,
            text="Cancel",
            command=self._cancel_event,
        )
        self.cancel_button.grid(row=2, column=1, padx=(20, 20), pady=(0, 20))

    def _ok_event(self, event=None) -> None:
        self._user_input = self.game_list_option_menu.get()
        self.grab_release()
        self.destroy()

    def _on_closing(self) -> None:
        self._user_input = ""
        self.grab_release()
        self.destroy()

    def _cancel_event(self) -> None:
        self._user_input = ""
        self.grab_release()
        self.destroy()

    def get_input(self) -> str:
        self.master.wait_window(self)
        return self._user_input


class ResetConversationWindow(customtkinter.CTkToplevel):
    def __init__(self) -> None:
        super().__init__()

        self._running: bool = False
        self._title = "Reset conversation"
        self._text = "Reset whole conversation?"
        self._reset_confirmed: bool
        self.title(self._title)
        self.lift()  # lift window on top
        self.attributes("-topmost", True)  # stay on top
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self._create_widgets()
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

    def _create_widgets(self) -> None:
        self.grid_columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        self.label = customtkinter.CTkLabel(
            master=self,
            width=300,
            wraplength=300,
            text=self._text,
        )
        self.label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self.ok_button = customtkinter.CTkButton(
            master=self, width=100, border_width=0, text="Ok", command=self._ok_event
        )
        self.ok_button.grid(row=2, column=0, padx=(20, 20), pady=(0, 20))

        self.cancel_button = customtkinter.CTkButton(
            master=self,
            width=100,
            border_width=0,
            text="Cancel",
            command=self._cancel_event,
        )
        self.cancel_button.grid(row=2, column=1, padx=(20, 20), pady=(0, 20))

    def _ok_event(self, event=None) -> None:
        self._reset_confirmed = True
        self.grab_release()
        self.destroy()

    def _on_closing(self) -> None:
        self._reset_confirmed = False
        self.grab_release()
        self.destroy()

    def _cancel_event(self) -> None:
        self._reset_confirmed = False
        self.grab_release()
        self.destroy()

    def get_input(self) -> bool:
        self.master.wait_window(self)
        return self._reset_confirmed


class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10

        self.tooltip_window = tkinter.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = tkinter.Label(
            self.tooltip_window,
            text=self.text,
            background="white",
            relief="solid",
            borderwidth=1,
        )
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
        self.tooltip_window = None
