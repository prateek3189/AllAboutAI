import tkinter as tk
import random
import collections # Used for deque for efficient snake body management

# --- Game Constants ---
GRID_SIZE = 20      # Size of each cell in pixels
WIDTH = 600         # Canvas width in pixels (must be a multiple of GRID_SIZE)
HEIGHT = 400        # Canvas height in pixels (must be a multiple of GRID_SIZE)
GAME_SPEED = 150    # Milliseconds between each game update (lower is faster)

# Colors
BACKGROUND_COLOR = "#000000"  # Black
SNAKE_COLOR = "#00FF00"       # Green
FOOD_COLOR = "#FF0000"        # Red
TEXT_COLOR = "#FFFFFF"        # White
GAME_OVER_COLOR = "#FFD700"   # Gold

class SnakeGame:
    def __init__(self, master):
        """
        Initializes the Snake Game.

        Args:
            master: The Tkinter root window.
        """
        self.master = master
        self.master.title("Python Snake Game")
        self.master.resizable(False, False) # Prevent resizing the window

        # Center the window on the screen
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width / 2) - (WIDTH / 2)
        y = (screen_height / 2) - (HEIGHT / 2)
        self.master.geometry(f'{WIDTH}x{HEIGHT+50}+{int(x)}+{int(y)}') # +50 for score/buttons

        # Create the game canvas
        self.canvas = tk.Canvas(master, bg=BACKGROUND_COLOR, width=WIDTH, height=HEIGHT)
        self.canvas.pack(pady=10)

        # Score display
        self.score_label = tk.Label(master, text="Score: 0", fg=TEXT_COLOR, bg=BACKGROUND_COLOR, font=("Inter", 16, "bold"))
        self.score_label.pack()

        # Game state variables
        self.snake = collections.deque() # Using deque for efficient append/pop from both ends
        self.food = None
        self.direction = 'Right' # Initial direction
        self.score = 0
        self.game_over_state = False
        self.game_running = False # To control the game loop

        # Bind arrow keys for movement
        self.master.bind("<Left>", lambda event: self.change_direction('Left'))
        self.master.bind("<Right>", lambda event: self.change_direction('Right'))
        self.master.bind("<Up>", lambda event: self.change_direction('Up'))
        self.master.bind("<Down>", lambda event: self.change_direction('Down'))
        # Bind 'R' key for restart
        self.master.bind("<r>", lambda event: self.reset_game())

        # Start button
        self.start_button = tk.Button(master, text="Start Game", command=self.start_game,
                                      font=("Inter", 14), bg="#4CAF50", fg="white",
                                      activebackground="#45a049", activeforeground="white",
                                      relief="raised", bd=3, padx=10, pady=5,
                                      cursor="hand2")
        self.start_button.pack(pady=5)

        self.reset_button = tk.Button(master, text="Reset Game (R)", command=self.reset_game,
                                       font=("Inter", 14), bg="#f44336", fg="white",
                                       activebackground="#da190b", activeforeground="white",
                                       relief="raised", bd=3, padx=10, pady=5,
                                       cursor="hand2")
        self.reset_button.pack(pady=5)
        self.reset_button.config(state=tk.DISABLED) # Disable until game starts or ends

        # Initial setup
        self.reset_game(initial_setup=True)


    def reset_game(self, initial_setup=False):
        """
        Resets the game to its initial state.
        """
        if self.game_running and not initial_setup:
            # If game is running and not initial setup, stop the current game loop
            self.master.after_cancel(self.game_loop_id)
            self.game_running = False

        self.canvas.delete("all") # Clear all drawn objects
        self.snake.clear()        # Clear snake segments
        self.food = None          # Clear food

        # Initial snake position (start in the middle, 3 segments)
        head_x = (WIDTH // 2 // GRID_SIZE) * GRID_SIZE
        head_y = (HEIGHT // 2 // GRID_SIZE) * GRID_SIZE
        for i in range(3):
            self.snake.appendleft((head_x - i * GRID_SIZE, head_y))

        self.direction = 'Right'
        self.score = 0
        self.score_label.config(text=f"Score: {self.score}")
        self.game_over_state = False
        self.place_food()
        self.create_objects()

        # Update button states
        self.start_button.config(state=tk.NORMAL)
        self.reset_button.config(state=tk.DISABLED if not self.game_running else tk.NORMAL)

    def start_game(self):
        """
        Starts the game loop.
        """
        if not self.game_running:
            self.game_running = True
            self.game_over_state = False # Ensure game over state is false
            self.start_button.config(state=tk.DISABLED) # Disable start button once game begins
            self.reset_button.config(state=tk.NORMAL) # Enable reset button
            self.game_loop()

    def create_objects(self):
        """
        Draws the snake and food on the canvas.
        """
        self.canvas.delete("snake") # Delete old snake segments
        for x, y in self.snake:
            self.canvas.create_rectangle(x, y, x + GRID_SIZE, y + GRID_SIZE,
                                         fill=SNAKE_COLOR, tags="snake", outline="black")

        self.canvas.delete("food") # Delete old food
        if self.food:
            x, y = self.food
            self.canvas.create_oval(x, y, x + GRID_SIZE, y + GRID_SIZE,
                                    fill=FOOD_COLOR, tags="food", outline="black")

    def move_snake(self):
        """
        Updates the snake's position based on its current direction.
        Handles food eating and collision detection.
        """
        if self.game_over_state or not self.game_running:
            return

        head_x, head_y = self.snake[0]
        new_head_x, new_head_y = head_x, head_y

        if self.direction == 'Up':
            new_head_y -= GRID_SIZE
        elif self.direction == 'Down':
            new_head_y += GRID_SIZE
        elif self.direction == 'Left':
            new_head_x -= GRID_SIZE
        elif self.direction == 'Right':
            new_head_x += GRID_SIZE

        new_head = (new_head_x, new_head_y)

        # Check for collisions before adding new head
        if self.check_collisions(new_head):
            self.game_over()
            return

        self.snake.appendleft(new_head) # Add new head

        # Check if food is eaten
        if new_head == self.food:
            self.score += 1
            self.score_label.config(text=f"Score: {self.score}")
            self.place_food() # Place new food
        else:
            self.snake.pop() # Remove tail if no food eaten

        self.create_objects() # Redraw snake and food

    def check_collisions(self, head):
        """
        Checks for collisions with walls or the snake's own body.

        Args:
            head: The (x, y) coordinates of the snake's new head.

        Returns:
            True if a collision occurs, False otherwise.
        """
        head_x, head_y = head

        # Wall collision
        if not (0 <= head_x < WIDTH and 0 <= head_y < HEIGHT):
            return True

        # Self-collision (check if new head is in any existing body segment)
        # Start checking from the 4th segment to avoid immediate self-collision on turns
        if head in list(self.snake)[1:]: # Convert deque to list for easier slicing
            return True

        return False

    def place_food(self):
        """
        Places food at a random valid position on the canvas.
        Ensures food does not spawn on the snake's body.
        """
        while True:
            x = random.randint(0, (WIDTH // GRID_SIZE) - 1) * GRID_SIZE
            y = random.randint(0, (HEIGHT // GRID_SIZE) - 1) * GRID_SIZE
            new_food_pos = (x, y)
            if new_food_pos not in self.snake: # Ensure food doesn't spawn on snake
                self.food = new_food_pos
                break

    def change_direction(self, new_direction):
        """
        Changes the snake's direction based on key press.
        Prevents the snake from immediately reversing direction.
        """
        if self.game_over_state or not self.game_running:
            return

        # Prevent immediate reversal
        if new_direction == 'Left' and self.direction != 'Right':
            self.direction = new_direction
        elif new_direction == 'Right' and self.direction != 'Left':
            self.direction = new_direction
        elif new_direction == 'Up' and self.direction != 'Down':
            self.direction = new_direction
        elif new_direction == 'Down' and self.direction != 'Up':
            self.direction = new_direction

    def game_over(self):
        """
        Handles the game over state: displays message and stops game loop.
        """
        self.game_over_state = True
        self.game_running = False
        self.canvas.create_text(WIDTH / 2, HEIGHT / 2, text="GAME OVER!",
                                font=("Inter", 36, "bold"), fill=GAME_OVER_COLOR, tags="game_over_text")
        self.canvas.create_text(WIDTH / 2, HEIGHT / 2 + 50, text=f"Final Score: {self.score}",
                                font=("Inter", 24, "bold"), fill=TEXT_COLOR, tags="final_score_text")
        self.start_button.config(state=tk.DISABLED) # Keep start button disabled
        self.reset_button.config(state=tk.NORMAL) # Enable reset button

    def game_loop(self):
        """
        The main game loop, called repeatedly to update game state.
        """
        if not self.game_over_state and self.game_running:
            self.move_snake()
            # Schedule the next update
            self.game_loop_id = self.master.after(GAME_SPEED, self.game_loop)
        elif self.game_over_state:
            # If game is over, ensure any pending after calls are cancelled
            if hasattr(self, 'game_loop_id'):
                self.master.after_cancel(self.game_loop_id)


# --- Main Application Entry Point ---
if __name__ == "__main__":
    root = tk.Tk()
    game = SnakeGame(root)
    root.mainloop()
