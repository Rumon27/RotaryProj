import tkinter as tk
from PIL import Image, ImageTk

TAG_PATH = "tags/tag_0.png"

def main():
    root = tk.Tk()
    root.title("ArUco Tkinter Test")
    root.geometry("500x500+100+100")   # width x height + x_offset + y_offset

    canvas = tk.Canvas(root, width=500, height=500, bg="white")
    canvas.pack()

    tag_img = Image.open(TAG_PATH)
    tk_img = ImageTk.PhotoImage(tag_img)

    canvas.create_image(250, 250, image=tk_img)  # centered on the canvas

    root.mainloop()

if __name__ == "__main__":
    main()