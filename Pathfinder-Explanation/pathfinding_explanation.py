import tkinter as tk
from math import dist
from random import randint

# todo needs a code cleanup, fix bug "AttributeError: 'Node' object has no attribute 'update'"
# Define colours
WALL_COLOUR = "black"
START_COLOUR = "#00b800"
END_COLOUR = "red"
EMPTY_COLOUR = "white"
PATH_COLOUR = "yellow"
OPEN_COLOUR = "#74DBEF"
CLOSED_COLOUR = "#5E88FC"


class Node:
    # Declare class level variables
    NODE_WIDTH = 65
    start_node = None
    end_node = None
    best_node = None

    def __init__(self, canvas, row, column, outline=True):
        # Initialise variables
        self.canvas = canvas
        self.row = row
        self.column = column
        self.colour = EMPTY_COLOUR
        self.clickable = True
        self.last_type = "empty"
        self.type = "empty"
        self.outline = "black" if outline else ""

        # Calculates x and y from row and column
        self.x = (column * self.NODE_WIDTH) + 2
        self.y = (row * self.NODE_WIDTH) + 2

        # Draws the node and stores the id
        self.rect = (self.x, self.y, self.x + Node.NODE_WIDTH, self.y + Node.NODE_WIDTH)
        self.id = [self.canvas.create_rectangle(*self.rect, fill=self.colour, outline=self.outline)]

        # Initialises start and end positions. These can be changed later.
        # By default the start and end points are 1 node in from the top left and 1 node in from the bottom right
        if self.row == self.column == 1:
            self.start()
        if self.row == int(PathfindingApp.CANVAS_HEIGHT / Node.NODE_WIDTH) - 2 and \
                self.column == int(PathfindingApp.CANVAS_WIDTH / Node.NODE_WIDTH) - 2:
            self.end()

        # Initialises pathfinding variables
        self.g_cost = 0
        self.h_cost = 0
        self.parent = None

    def draw(self):  # Will delete the node and then redraw it on the canvas. Returns node id
        [self.canvas.delete(i) for i in self.id]
        self.id = [self.canvas.create_rectangle(*self.rect, fill=self.colour, outline=self.outline)]

        if self.colour == OPEN_COLOUR:
            self.id.append(self.draw_arrow())
            if str(type(PathfindingApp.algorithm)) == "<class '__main__.AStarSearch'>":
                self.id.append(self.canvas.create_text(self.x + 12, self.y + Node.NODE_WIDTH - 10, text=self.g_cost))
                self.id.append(self.canvas.create_text(self.x + Node.NODE_WIDTH - 15, self.y + Node.NODE_WIDTH - 10,
                                                       text=round(self.h_cost)))
            self.id.append(self.canvas.create_text(self.x + Node.NODE_WIDTH / 2, self.y + Node.NODE_WIDTH / 2,
                                                   text=round(self.h_cost + self.g_cost), font="10"))
            if Node.best_node == self:
                self.id.append(self.canvas.create_oval(self.x + 10, self.y + 15, self.x + Node.NODE_WIDTH - 10,
                                                       self.y + Node.NODE_WIDTH - 15, outline=PATH_COLOUR))
        if self.colour == CLOSED_COLOUR:
            self.draw_arrow(big=True)

    def reset(self):  # Resets empty nodes colour. Function used after a visualisation
        if self.type == "empty":
            self.colour = EMPTY_COLOUR
            self.draw()
            self.g_cost = 0
            self.h_cost = 0
            self.parent = None

    def wall(self):  # Changes node colour after being drawn on. Either to wall or empty depending on its previous state
        if self.colour == EMPTY_COLOUR and self.clickable:
            self.colour = WALL_COLOUR
            self.draw()
            self.clickable = False
            self.type = "wall"
            self.last_type = "wall"
        elif self.colour == WALL_COLOUR and self.clickable:
            self.colour = EMPTY_COLOUR
            self.draw()
            self.clickable = False
            self.type = "empty"
            self.last_type = "empty"

    def move_cost(self, other):  # Calculates the g_cost to move to that cell. 10 for adjacent, 14 for diagonals
        if self.row == other.row or self.column == other.column:
            return 10  # Adjacent nodes have a 10 g_cost
        else:
            return 14  # Diagonally adjacent nodes have a 14 g_cost

    def path(self):  # Will turn any node into a path node
        self.colour = PATH_COLOUR
        self.draw()

    def open(self):  # Will turn any node into an open node
        self.colour = OPEN_COLOUR
        self.draw()

    def closed(self):  # Will turn any node into a closed node
        self.colour = CLOSED_COLOUR
        self.draw()

    def start(self):  # Will turn any node into the start node
        self.type = "start"
        self.colour = START_COLOUR
        Node.start_node = self
        self.draw()

    def end(self):  # Will turn any node into the end node
        self.type = "end"
        self.colour = END_COLOUR
        Node.end_node = self
        self.draw()

    def clear(self):  # Will return node to its previous form
        # Resets self.type to the last type that the cell was
        self.type = self.last_type

        if self.type == "empty":
            self.colour = EMPTY_COLOUR
        elif self.type == "wall":
            self.colour = WALL_COLOUR
        self.draw()

    def draw_arrow(self, big=False):
        if self.parent.row < self.row and self.parent.column < self.column:
            if big:
                self.id.append(self.canvas.create_line(self.x + 10, self.y + 10, self.x + Node.NODE_WIDTH - 10,
                                                       self.y + Node.NODE_WIDTH - 10, arrow=tk.FIRST, width=3))
            else:
                self.id.append(self.canvas.create_line(self.x, self.y, self.x + 20, self.y + 20, arrow=tk.FIRST))
        elif self.parent.row < self.row and self.parent.column > self.column:
            if big:
                self.id.append(self.canvas.create_line(self.x + 10, self.y + Node.NODE_WIDTH - 10,
                                                       self.x + Node.NODE_WIDTH - 10, self.y + 10, arrow=tk.LAST,
                                                       width=3))
            else:
                self.id.append(self.canvas.create_line(self.x + Node.NODE_WIDTH, self.y, self.x + Node.NODE_WIDTH - 20,
                                                       self.y + 20, arrow=tk.FIRST))
        elif self.parent.column < self.column and self.parent.row > self.row:
            if big:
                self.id.append(self.canvas.create_line(self.x + 10, self.y + Node.NODE_WIDTH - 10,
                                                       self.x + Node.NODE_WIDTH - 10, self.y + 10, arrow=tk.FIRST,
                                                       width=3))
            else:
                self.id.append(self.canvas.create_line(self.x + Node.NODE_WIDTH, self.y, self.x + Node.NODE_WIDTH - 20,
                                                       self.y + 20, arrow=tk.LAST))
        elif self.parent.row > self.row and self.parent.column > self.column:
            if big:
                self.id.append(self.canvas.create_line(self.x + 10, self.y + 10, self.x + Node.NODE_WIDTH - 10,
                                                       self.y + Node.NODE_WIDTH - 10, arrow=tk.LAST, width=3))
            else:
                self.id.append(self.canvas.create_line(self.x, self.y, self.x + 20, self.y + 20, arrow=tk.LAST))
        elif self.parent.row < self.row:
            if big:
                self.id.append(self.canvas.create_line(self.x + Node.NODE_WIDTH / 2, self.y + 10, self.x +
                                                       Node.NODE_WIDTH / 2, self.y + Node.NODE_WIDTH - 10,
                                                       arrow=tk.FIRST, width=3))
            else:
                self.id.append(self.canvas.create_line(self.x + Node.NODE_WIDTH / 2, self.y,
                                                       self.x + Node.NODE_WIDTH / 2, self.y + 20, arrow=tk.FIRST))
        elif self.parent.row > self.row:
            if big:
                self.id.append(self.canvas.create_line(self.x + Node.NODE_WIDTH / 2, self.y + 10,
                                                       self.x + Node.NODE_WIDTH / 2, self.y + Node.NODE_WIDTH - 10,
                                                       arrow=tk.LAST, width=3))
            else:
                self.id.append(self.canvas.create_line(self.x + Node.NODE_WIDTH / 2, self.y,
                                                       self.x + Node.NODE_WIDTH / 2, self.y + 20, arrow=tk.LAST))
        elif self.parent.column < self.column:
            if big:
                self.id.append(self.canvas.create_line(self.x + 10, self.y + Node.NODE_WIDTH / 2 - 2,
                                                       self.x + Node.NODE_WIDTH - 10, self.y + Node.NODE_WIDTH / 2 - 2,
                                                       arrow=tk.FIRST, width=3))
            else:
                self.id.append(self.canvas.create_line(self.x + Node.NODE_WIDTH / 2 - 10, self.y + 10,
                                                       self.x + Node.NODE_WIDTH / 2 + 10, self.y + 10, arrow=tk.FIRST))
        elif self.parent.column > self.column:
            if big:
                self.id.append(self.canvas.create_line(self.x + 10, self.y + Node.NODE_WIDTH / 2 - 2,
                                                       self.x + Node.NODE_WIDTH - 10, self.y + Node.NODE_WIDTH / 2 - 2,
                                                       arrow=tk.LAST, width=3))
            else:
                self.id.append(self.canvas.create_line(self.x + Node.NODE_WIDTH / 2 - 10, self.y + 10,
                                                       self.x + Node.NODE_WIDTH / 2 + 10, self.y + 10, arrow=tk.LAST))


class AStarSearch:  # Handles A* search algorithm to complete the maze
    def __init__(self, grid, canvas, diagonals):
        # Initialise variables
        self.grid = grid
        self.canvas = canvas
        self.diagonals = diagonals

        # Open_set contains nodes to be tested and closed_set contains nodes that have been tested
        self.open_set = set()
        self.closed_set = set()

        # Pathfinding starts by adding the start node to the open set
        self.current = Node.start_node
        self.open_set.add(self.current)

    def a_star_search(self):  # Runs A* search algorithm
        if self.current == Node.end_node:
            path = []
            while self.current.parent:  # Calculates path by tracing back through parent nodes
                path.append(self.current)
                self.current = self.current.parent
            path.append(self.current)
            return path[::-1]  # reverses the output list

        self.open_set.remove(self.current)
        self.closed_set.add(self.current)

        for node in self.children(self.current, diagonals=self.diagonals):  # Loops over neighbouring nodes
            if node in self.closed_set:
                continue  # Skips if node is already in closed set
            if node in self.open_set:
                new_g = self.current.g_cost + self.current.move_cost(node)
                if node.g_cost > new_g:  # If the new g cost is lower it gets replaced
                    node.g_cost = new_g
                    node.parent = self.current
            else:
                # G cost and H cost of the node is calculated
                node.g_cost = self.current.g_cost + self.current.move_cost(node)
                node.h_cost = dist([node.x, node.y], [Node.end_node.x, Node.end_node.y])

                # Sets node parent
                node.parent = self.current
                self.open_set.add(node)

                if node != node.end_node:
                    node.open()

        if self.current != Node.start_node:
            self.current.closed()

        if not self.open_set:
            return "no solution"

        # Finds lowest item by f cost (g cost + h cost)
        self.current = min(self.open_set, key=lambda n: n.g_cost + n.h_cost)
        Node.best_node = self.current
        Node.best_node.update()

    def children(self, node, diagonals=False):  # Will return neighbouring nodes
        row = node.row
        column = node.column
        links = []

        # As long as the node is not off the grid then it will add it to the links list
        if row != len(self.grid) - 1:
            links.append(self.grid[row + 1][column])
        if row != 0:
            links.append(self.grid[row - 1][column])
        if column != len(self.grid[0]) - 1:
            links.append(self.grid[row][column + 1])
        if column != 0:
            links.append(self.grid[row][column - 1])
        if diagonals:
            if row != len(self.grid) - 1 and column != len(self.grid[0]) - 1:
                links.append(self.grid[row + 1][column + 1])
            if row != len(self.grid) - 1 and column != 0:
                links.append(self.grid[row + 1][column - 1])
            if row != 0 and column != len(self.grid[0]) - 1:
                links.append(self.grid[row - 1][column + 1])
            if row != 0 and column != 0:
                links.append(self.grid[row - 1][column - 1])
        return [link for link in links if link.type != "wall"]  # Returns all nodes that are not walls


class DijkstraAlgorithm:
    def __init__(self, grid, canvas, diagonals):
        # Initialise variables
        self.grid = grid
        self.canvas = canvas
        self.diagonals = diagonals

        # Open_set contains nodes to be tested and closed_set contains nodes that have been tested
        self.open_set = set()
        self.closed_set = set()

        # Pathfinding starts by adding the start node to the open set
        self.current = Node.start_node
        self.open_set.add(self.current)

    def dijkstra_algorithm(self):  # Runs Dijkstra's algorithm search algorithm
        if self.current == Node.end_node:
            path = []
            while self.current.parent:  # Calculates path by tracing back through parent nodes
                path.append(self.current)
                self.current = self.current.parent
            path.append(self.current)
            return path[::-1]  # reverses the output list

        self.open_set.remove(self.current)
        self.closed_set.add(self.current)

        for node in self.children(self.current, diagonals=self.diagonals):  # Loops over neighbouring nodes
            if node in self.closed_set:
                continue  # Skips if node is already in closed set
            if node in self.open_set:
                new_g = self.current.g_cost + self.current.move_cost(node)
                if node.g_cost > new_g:  # If the new g cost is lower it gets replaced
                    node.g_cost = new_g
                    node.parent = self.current
            else:
                # G cost and H cost of the node is calculated
                node.g_cost = self.current.g_cost + self.current.move_cost(node)

                # Sets node parent
                node.parent = self.current
                self.open_set.add(node)

                if node != node.end_node:
                    node.open()

        if self.current != Node.start_node:
            self.current.closed()

        if not self.open_set:
            return "no solution"

        # Finds lowest item by f cost (g cost + h cost)
        self.current = min(self.open_set, key=lambda n: n.g_cost)
        Node.best_node = self.current
        Node.best_node.update()

    def children(self, node, diagonals=False):  # Will return neighbouring nodes
        row = node.row
        column = node.column
        links = []

        # As long as the node is not off the grid then it will add it to the links list
        if row != len(self.grid) - 1:
            links.append(self.grid[row + 1][column])
        if row != 0:
            links.append(self.grid[row - 1][column])
        if column != len(self.grid[0]) - 1:
            links.append(self.grid[row][column + 1])
        if column != 0:
            links.append(self.grid[row][column - 1])
        if diagonals:
            if row != len(self.grid) - 1 and column != len(self.grid[0]) - 1:
                links.append(self.grid[row + 1][column + 1])
            if row != len(self.grid) - 1 and column != 0:
                links.append(self.grid[row + 1][column - 1])
            if row != 0 and column != len(self.grid[0]) - 1:
                links.append(self.grid[row - 1][column + 1])
            if row != 0 and column != 0:
                links.append(self.grid[row - 1][column - 1])
        return [link for link in links if link.type != "wall"]  # Returns all nodes that are not walls


class PathfindingApp:  # Handles the main application and tkinter widgets
    # define class variables and constants
    CANVAS_WIDTH = 1237
    CANVAS_HEIGHT = 587
    CANVAS_BG = "white"
    algorithm = None

    def __init__(self):
        # Initialise variables
        self.drag_start = False
        self.drag_end = False
        self.display_path = False
        self.path = []
        self.complete = False

        # Setup the main window
        self.root = tk.Tk()
        self.root.title("Pathfinding Explanation")
#        self.root.state("zoomed")

        # Create buttons and widgets
        self.info_btn = tk.Button(self.root, text="ⓘ", command=self.info_popup)
        self.info_btn.grid(row=0, column=0, sticky=tk.W)

        algorithms = ["A* Search", "Dijkstra's Algorithm"]
        self.algorithm_option = tk.StringVar(self.root)
        self.algorithm_option.set(algorithms[0])  # sets default algorithm to A* search
        self.algorithms_menu = tk.OptionMenu(self.root, self.algorithm_option, *algorithms)
        self.algorithms_menu.grid(row=0, column=1, pady=0)

        self.maze_btn = tk.Button(self.root, text="Maze: Random", command=lambda: self.generate_random_maze(3))
        self.maze_btn.grid(row=0, column=2)

        self.clear_btn = tk.Button(self.root, text="clear", command=self.erase_popup)
        self.clear_btn.grid(row=0, column=3)

        self.diagonals_value = tk.BooleanVar()
        self.diagonals_value.set(False)
        self.diagonals_checkbutton = tk.Checkbutton(self.root, text="Allow diagonals", activebackground="white",
                                                    var=self.diagonals_value)
        self.diagonals_checkbutton.grid(row=0, column=4)

        self.stop_btn = tk.Button(self.root, text="stop", command=self.remove_path)
        self.stop_btn["state"] = tk.DISABLED
        self.stop_btn.grid(row=0, column=5)

        self.credits = tk.Label(self.root, text="Created by George (William) Stuart 2021")
        self.credits.grid(row=2, column=0, sticky=tk.W, columnspan=2)

        # Create the canvas that will hold the nodes
        self.canvas = tk.Canvas(self.root, width=self.CANVAS_WIDTH, height=self.CANVAS_HEIGHT, bg=self.CANVAS_BG)
        self.canvas.grid(row=1, column=0, columnspan=6, padx=13)

        # Create key binding for the canvas
        self.canvas.bind("<B1-Motion>", self.b1_motion)
        self.canvas.bind("<Button-1>", self.b1_pressed)
        self.canvas.bind("<ButtonRelease-1>", self.b1_release)
        self.root.bind("<KeyPress-space>", self.find_path)

        # Generate a grid of node objects
        self.grid = self.generate_grid()

        # Run the main loop
        self.root.mainloop()

    def find_path(self, _):  # Will find the path using the algorithm selected.
        if self.complete:
            return
        if self.path:
            self.path[-1].path()
            self.path.pop()
            if not self.path:
                self.complete = True
        elif self.display_path:
            path = []

            if str(type(PathfindingApp.algorithm)) == "<class '__main__.AStarSearch'>":
                path = PathfindingApp.algorithm.a_star_search()
            if str(type(PathfindingApp.algorithm)) == "<class '__main__.DijkstraAlgorithm'>":
                path = PathfindingApp.algorithm.dijkstra_algorithm()

            # Draws the path if there is a solution
            if path:
                if path == "no solution":
                    self.no_solution()  # Will create the no solution popup
                    self.complete = True
                else:
                    self.path = [node for node in path[1:-1]]
                    self.path[-1].path()
                    self.path.pop()
        else:
            # Disables buttons
            self.clear_btn["state"] = tk.DISABLED
            self.stop_btn["state"] = tk.NORMAL
            self.maze_btn["state"] = tk.DISABLED
            self.algorithms_menu["state"] = tk.DISABLED
            self.diagonals_checkbutton["state"] = tk.DISABLED
            self.stop_btn.config(fg="red")

            self.display_path = True
            path = []

            # Check for which algorithm has been selected
            if self.algorithm_option.get() == "A* Search":
                PathfindingApp.algorithm = AStarSearch(self.grid, self.canvas, self.diagonals_value.get())
                path = PathfindingApp.algorithm.a_star_search()
            elif self.algorithm_option.get() == "Dijkstra's Algorithm":
                PathfindingApp.algorithm = DijkstraAlgorithm(self.grid, self.canvas, self.diagonals_value.get())
                path = PathfindingApp.algorithm.dijkstra_algorithm()

            # Draws the path if there is a solution
            if path:
                if path == "no solution":
                    self.no_solution()  # Will create the no solution popup
                else:
                    self.path = [node for node in path[1:-1]]
                    self.path[-1].path()
                    self.path.pop()

    def generate_grid(self):  # Clears canvas and then generates a board of nodes
        self.canvas.delete("all")
        return [[Node(self.canvas, y, x)
                for x in range(int(self.CANVAS_WIDTH / Node.NODE_WIDTH))]
                for y in range(int(self.CANVAS_HEIGHT / Node.NODE_WIDTH))]

    def generate_random_maze(self, chance):
        # Remembers start and end node positions
        start = Node.start_node.row, Node.start_node.column
        end = Node.end_node.row, Node.end_node.column

        # Resets the grid
        self.reset()

        # Create the start and end nodes
        Node.start_node.clear()
        Node.start_node = self.grid[start[0]][start[1]]
        Node.start_node.start()
        Node.end_node.clear()
        Node.end_node = self.grid[end[0]][end[1]]
        Node.end_node.end()

        # Loops over nodes and randomly selects them to become wall nodes
        for x in range(len(self.grid)):
            for y in range(len(self.grid[x])):
                if randint(0, chance) == 0:
                    self.grid[x][y].wall()

    def b1_pressed(self, event):  # Handles left click presses
        # Calculates the row and column of the click
        row = int(event.y / Node.NODE_WIDTH)
        column = int(event.x / Node.NODE_WIDTH)

        # Check's whether the user has clicked on the start or end node. If not, the user is drawing.
        if row == Node.start_node.row and column == Node.start_node.column and not self.display_path:
            self.drag_start = True
        elif row == Node.end_node.row and column == Node.end_node.column and not self.display_path:
            self.drag_end = True
        else:
            if not self.display_path:  # Prevents the user from drawing while the visualisation is in progress
                self.draw(event)

    def b1_motion(self, event):  # Handles mouse movement
        if self.drag_start:  # If the user is dragging the start point
            # Calculates the row and column of the click
            row = int(event.y / Node.NODE_WIDTH)
            column = int(event.x / Node.NODE_WIDTH)

            # Prevents user from dragging over the end node
            if row != Node.end_node.row or column != Node.end_node.column:
                # Prevents user from dragging the start node off the canvas
                if len(self.grid) - 1 >= row >= 0 and len(self.grid[0]) - 1 >= column >= 0:
                    # Clears the old start node, reassigns the new start node and draws it on the canvas
                    Node.start_node.clear()
                    Node.start_node = self.grid[row][column]
                    Node.start_node.start()
        elif self.drag_end:  # If the user is dragging the end point
            # Calculates the row and column of the click
            row = int(event.y / Node.NODE_WIDTH)
            column = int(event.x / Node.NODE_WIDTH)

            # Prevents user from dragging over the start node
            if row != Node.start_node.row or column != Node.start_node.column:
                # Prevents user from dragging the start node off the canvas
                if len(self.grid) - 1 >= row >= 0 and len(self.grid[0]) - 1 >= column >= 0:
                    # Clears the old end node, reassigns the new end node and draws it on the canvas
                    Node.end_node.clear()
                    Node.end_node = self.grid[row][column]
                    Node.end_node.end()
        else:
            if not self.display_path:   # Prevents the user from drawing while the visualisation is in progress
                self.draw(event)

    def b1_release(self, _):  # Handles the release of the left click
        # Resets dragging
        self.drag_start = False
        self.drag_end = False
        self.nodes_clickable()

    def draw(self, event):  # Will turn the nodes that have been drawn on into wall nodes
        # Calculates the row and column of the click
        row = int(event.y / Node.NODE_WIDTH)
        column = int(event.x / Node.NODE_WIDTH)

        # Prevents the user drawing off the canvas
        if len(self.grid) - 1 >= row >= 0 and len(self.grid[0]) - 1 >= column >= 0:
            self.grid[row][column].wall()  # Turns nodes into wall nodes

    def nodes_clickable(self):  # Will set all nodes to clickable
        for x in range(len(self.grid)):
            for y in range(len(self.grid[x])):
                self.grid[x][y].clickable = True

    def erase_popup(self):  # Generates a popup asking user if they are sure they want to clear
        # Creates the popup window
        popup = tk.Tk()
        popup.title("")
        popup.resizable(False, False)

        # Adds widgets to the popup
        tk.Label(popup, text="Are you sure you want to erase all?").grid(row=0, column=0, columnspan=2)
        tk.Button(popup, text="yes",
                  command=lambda: PathfindingApp.delete_popup(popup, self.reset)).grid(row=1, column=0)
        tk.Button(popup, text="no", command=popup.destroy).grid(row=1, column=1)

    def reset(self):  # Resets the grid
        self.grid = self.generate_grid()

    def remove_path(self):  # Removes the open and closed nodes generated by the visualisation
        # Resets variables
        self.display_path = False
        self.path = []
        self.maze_btn["state"] = tk.NORMAL
        self.clear_btn["state"] = tk.NORMAL
        self.stop_btn["state"] = tk.DISABLED
        self.algorithms_menu["state"] = tk.NORMAL
        self.diagonals_checkbutton["state"] = tk.NORMAL
        self.stop_btn.config(fg="black")
        self.complete = False

        # Loops over each nodes and resets it
        for x in range(len(self.grid)):
            for y in range(len(self.grid[x])):
                self.grid[x][y].reset()

    def no_solution(self):  # Creates a popup if the maze has no solution
        self.complete = True

        # Creates the popup window
        popup = tk.Tk()
        popup.title("")
        popup.resizable(False, False)

        # Adds widgets to the popup
        tk.Label(popup, text="There is no solution to this maze").grid(row=0, column=0)
        tk.Button(popup, text="ok",
                  command=lambda: PathfindingApp.delete_popup(popup, self.remove_path)).grid(row=1, column=0)

    @staticmethod
    def delete_popup(popup, command):  # Deletes the popup and runs a command
        popup.destroy()
        command()

    @staticmethod
    def info_popup():  # Creates the information popup
        # Creates the popup window
        popup = tk.Tk()
        popup.title("Info")
        popup.resizable(False, False)

        # Adds widgets to the popup
        tk.Label(popup, text="Welcome to pathfinding visualiser\n", font="none 12").grid(row=0, column=0, columnspan=2,
                                                                                         padx=30)
        tk.Label(popup, text="Basic controls:", font="none 11",
                 justify=tk.LEFT).grid(row=1, column=0, sticky=tk.W, columnspan=2)

        tk.Label(popup,
                 text="""        Drag start and end points as you wish
        Click to add walls
        Select an algorithm
        Press space for a step by step visualisation""",
                 justify=tk.LEFT, font="none 10").grid(row=2, column=0, columnspan=2, sticky=tk.W)

        tk.Label(popup, text="\nExplanation:", font="none 11",
                 justify=tk.LEFT).grid(row=3, column=0, sticky=tk.W, columnspan=2)

        tk.Label(popup, text="""        On each node the bottom left number is it's g cost,
        the bottom right number is the h cost and the middle number is the f cost
        The arrows at the top of the nodes show who their parent node is.
        A yellow circle signifies that it is the node with the lowest f cost""", font="none 10",
                 justify=tk.LEFT).grid(row=4, column=0, sticky=tk.E)

        tk.Label(popup, text="\nColours:", font="none 11",
                 justify=tk.LEFT).grid(row=5, column=0, sticky=tk.W, columnspan=2)

        tk.Label(popup, text="""        White: unvisited node
        Light Blue: visited node
        Blue: Tested node
        Yellow: Path node""", font="none 10",
                 justify=tk.LEFT).grid(row=6, column=0, sticky=tk.W)

        tk.Button(popup, text="ok", command=popup.destroy).grid(row=7, column=0, columnspan=2)


if __name__ == '__main__':
    PathfindingApp()
