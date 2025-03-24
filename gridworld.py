import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class Gridworld:
    def __init__(self, size, guard_positions):
        self.size = size
        self.guard_positions = guard_positions
        self.attacker_position = (0, 0)  # Start at top-left
        self.goal_position = (size - 1, size - 1)  # Exit at bottom-right
    
    def display(self):
        plt.figure(figsize=(6,6))
        grid_numeric = np.zeros((self.size, self.size))
        for i in range(self.size):
            for j in range(self.size):
                if (i, j) == self.attacker_position:
                    grid_numeric[i, j] = 2  # Attacker (Red)
                elif (i, j) == self.goal_position:
                    grid_numeric[i, j] = 3  # Exit (Green)
                elif (i, j) in self.guard_positions:
                    grid_numeric[i, j] = 1  # Guard (Blue)
        
        cmap = sns.color_palette(["white", "blue", "red", "green"])  # Define colors
        sns.heatmap(grid_numeric, annot=False, cmap=cmap, cbar=False, linewidths=1, linecolor='black', 
                    xticklabels=False, yticklabels=False)
        plt.title("Gridworld Museum")
        plt.show()
    
    def move_attacker(self, new_position):
        if self._is_valid_move(new_position):
            self.attacker_position = new_position  # Update attacker position
        
    def _is_valid_move(self, position):
        x, y = position
        return 0 <= x < self.size and 0 <= y < self.size and position not in self.guard_positions


grid_size = 5
guard_positions = [(1, 3), (3, 2)]
gw = Gridworld(grid_size, guard_positions)
gw.display()
