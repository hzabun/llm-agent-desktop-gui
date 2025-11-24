import random

import customtkinter as ctk

from src.llm_agent_gui.utils import prompts


class TicTacToe(ctk.CTkFrame):
    def __init__(self, master, main_app, **kwargs):
        super().__init__(master, **kwargs)

        self.initial_game_session = True
        self.consecutive_game_session = False
        self.main_app = main_app
        self.user_mark = "X"
        self.assistant_mark = "O"
        self.board = [""] * 9
        self.buttons = []
        self.user_wins = 0
        self.ai_wins = 0
        self.actions_taken = ""

        self.create_widgets()

    def create_widgets(self):
        self.status_label = ctk.CTkLabel(
            self, text="Player X's turn", font=("Arial", 16)
        )
        self.status_label.pack(pady=10)

        frame = ctk.CTkFrame(self)
        frame.pack()

        for i in range(9):
            button = ctk.CTkButton(
                frame,
                text="",
                width=90,
                height=90,
                font=("Arial", 24),
                command=lambda i=i: self.user_move(i),
            )
            button.grid(row=i // 3, column=i % 3, padx=5, pady=5)
            self.buttons.append(button)

        self.reset_button = ctk.CTkButton(self, text="Quit", command=self.quit_game)
        self.reset_button.pack(pady=10)

        self.reset_button = ctk.CTkButton(self, text="Restart", command=self.reset_game)
        self.reset_button.pack(pady=10)

    def user_move(self, index):
        if self.board[index] == "" and not self.check_winner():
            self.board[index] = self.user_mark
            self.buttons[index].configure(text=self.user_mark)

            if self.check_winner():
                self.status_label.configure(text=f"Player {self.user_mark} wins!")
                self.user_wins += 1
            elif "" not in self.board:
                self.status_label.configure(text="It's a tie!")
            else:
                self.play_game()

    def ai_move(self):
        # Adding random noise with 30% chance to make a random move instead of the optimal one
        if random.random() < 0.3:
            available_moves = [i for i in range(9) if self.board[i] == ""]
            best_move = random.choice(available_moves)
        else:
            best_score = -float("inf")
            best_move = None

            for i in range(9):
                if self.board[i] == "":
                    self.board[i] = "O"
                    score = self.minimax(self.board, 0, False)
                    self.board[i] = ""
                    if score > best_score:
                        best_score = score
                        best_move = i

        if best_move is not None:
            self.board[best_move] = self.assistant_mark
            self.buttons[best_move].configure(text=self.assistant_mark)
            if self.check_winner():
                self.status_label.configure(text=f"Player {self.assistant_mark} wins!")
                self.ai_wins += 1
            elif "" not in self.board:
                self.status_label.configure(text="It's a tie!")
            else:
                self.status_label.configure(text=f"Player {self.user_mark}'s turn")

    def minimax(self, board, depth, is_maximizing):
        winner = self.check_winner()
        if winner:
            return 1 if winner == self.assistant_mark else -1
        if "" not in board:
            return 0

        if is_maximizing:
            best_score = -float("inf")
            for i in range(9):
                if board[i] == "":
                    board[i] = self.assistant_mark
                    score = self.minimax(board, depth + 1, False)
                    board[i] = ""
                    best_score = max(score, best_score)
            return best_score
        else:
            best_score = float("inf")
            for i in range(9):
                if board[i] == "":
                    board[i] = self.user_mark
                    score = self.minimax(board, depth + 1, True)
                    board[i] = ""
                    best_score = min(score, best_score)
            return best_score

    def check_board(self) -> str:
        human_can_win = False
        ai_can_win = False

        for i in range(9):
            if self.board[i] == "":
                # Check for user win
                self.board[i] = "X"
                if self.check_winner() == "X":
                    human_can_win = True
                self.board[i] = ""

                # Check for AI win
                self.board[i] = "O"
                if self.check_winner() == "O":
                    ai_can_win = True
                self.board[i] = ""

        if human_can_win and ai_can_win:
            return "Both you and the user can win the game with the next move."
        elif human_can_win:
            return "The user can win the game with the next move."
        elif ai_can_win:
            return "You can win the game with the next move."
        else:
            return "Neither you nor the user has an immediate win available."

    def check_winner(self):
        winning_combinations = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],  # Rows
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],  # Columns
            [0, 4, 8],
            [2, 4, 6],  # Diagonals
        ]

        for combo in winning_combinations:
            if (
                self.board[combo[0]]
                == self.board[combo[1]]
                == self.board[combo[2]]
                != ""
            ):
                return self.board[combo[0]]

        return None

    def quit_game(self):
        current_summary = (
            self.main_app.character_agent.summary_buffer_memory.load_summary_from_disk()
        )

        game_quit_prompt = prompts.prepare_game_quit_prompt(
            character=self.main_app.character_agent.character,
            game="Tic-Tac-Toe",
            ai_wins=self.ai_wins,
            user_wins=self.user_wins,
            system_message=self.main_app.character_agent.initial_system_message,
            current_summary=current_summary,
        )

        charater_reaction = self.main_app.character_agent.llm.inference_llm(
            prompt=[{"role": "system", "content": game_quit_prompt}]
        )

        self.main_app.add_agent_answer_to_chat_history(
            character_response=charater_reaction
        )

        provisional_user_message = f"We just finished our Tic-Tac-Toe game session. I won {self.user_wins} times and you won {self.ai_wins} time."
        self.main_app.update_character_agent_memory(
            prompt=provisional_user_message, agent_answer=charater_reaction
        )

        self.main_app.character_image_game_frame.tic_tac_toe.grid_remove()

    def reset_game(self):
        self.board = [""] * 9
        self.user_mark = "X"
        self.status_label.configure(text="Player X's turn")

        for button in self.buttons:
            button.configure(text="")

        self.actions_taken = ""
        self.initial_game_session = False
        self.consecutive_game_session = True

    def play_game(self) -> None:
        checked_board = False

        if self.initial_game_session:
            current_summary = self.main_app.character_agent.summary_buffer_memory.load_summary_from_disk()

            game_start_prompt = prompts.prepare_game_start_prompt(
                user_name=self.main_app.character_agent.name_of_user,
                game="Tic-Tac-Toe",
                roleplay_instructions=self.main_app.character_agent.initial_system_message,
                current_summary=current_summary,
                action_log=self.actions_taken,
            )
            self.game_prompt = {"role": "system", "content": game_start_prompt}

        elif self.consecutive_game_session:
            current_summary = self.main_app.character_agent.summary_buffer_memory.load_summary_from_disk()
            game_continue_prompt = prompts.prepare_game_continue_prompt(
                user_name=self.main_app.character_agent.name_of_user,
                game="Tic-Tac-Toe",
                roleplay_instructions=self.main_app.character_agent.initial_system_message,
                current_summary=current_summary,
                ai_wins=self.ai_wins,
                user_wins=self.user_wins,
                action_log="",
            )
            self.game_prompt = {"role": "system", "content": game_continue_prompt}
            self.user_wins = 0
            self.ai_wins = 0
        while True:
            character_action_step = self.main_app.character_agent.llm.inference_llm(
                [self.game_prompt]
            )
            print(character_action_step)

            clean_character_action_step = (
                self.main_app.character_agent.clean_agent_response(
                    character_action_step
                )
            )
            action, action_input = (
                self.main_app.character_agent.extract_action_and_input(
                    clean_character_action_step
                )
            )
            if action[-1] == "Make move":
                self.ai_move()
                clean_character_action_step += f"\nResult of move: You made a move and then {self.main_app.character_agent.name_of_user} made his move.\n"
                self.actions_taken += clean_character_action_step
                break
            elif action[-1] == "Check board":
                if not checked_board:
                    action_result = self.check_board()
                    clean_character_action_step += f"\nBoard status: {action_result}\n"
                    self.actions_taken += clean_character_action_step
                    checked_board = True
                else:
                    self.ai_move()
                    clean_character_action_step += f"\nResult of move: You made a move and then {self.main_app.character_agent.name_of_user} made his move.\n"
                    self.actions_taken += clean_character_action_step
                    break
            elif action[-1] == "Respond to user":
                self.main_app.add_agent_answer_to_chat_history(
                    character_response=action_input[0]
                )
                self.actions_taken += "\n" + clean_character_action_step + "\n"
