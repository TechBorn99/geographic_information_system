from tkinter import *


class GeographicInformationSystem:

    root = Tk()

    def __init__(self):

        self.root.title('Geographic information system')
        self.root.iconbitmap(r".\resources\flaticon.ico")

        self.root.geometry("1536x764+0+0")

        self.root.resizable(0, 0)

        self.root.columnconfigure(0, weight=4)
        self.root.columnconfigure(1, weight=4)
        self.root.rowconfigure(0, weight=1)

        self.raster_side = Frame(self.root, bg='lightgoldenrod1')
        self.vector_side = Frame(self.root, bg='lightgoldenrod1')

        self.raster_side.grid(row=0, column=0, sticky="nsew")
        self.vector_side.grid(row=0, column=1, sticky="nsew")

        self.root.mainloop()


if __name__ == '__main__':
    start = GeographicInformationSystem()
