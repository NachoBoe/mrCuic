import tkinter as tk

class DragDropApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Drag and Drop Example")

        self.label = tk.Label(self, text="Drag me", bg="lightblue", width=10, height=5)
        self.label.place(x=50, y=50)

        self.label.bind("<Button-1>", self.start_drag)
        self.label.bind("<B1-Motion>", self.do_drag)

    def start_drag(self, event):
        self.drag_data = {"x": event.x, "y": event.y}

    def do_drag(self, event):
        x = self.winfo_pointerx() - self.drag_data["x"]
        y = self.winfo_pointery() - self.drag_data["y"]
        self.label.place(x=x, y=y)

if __name__ == "__main__":
    app = DragDropApp()
    app.geometry("400x300")
    app.mainloop()
