import tkinter as tk
import tkinter.font





if __name__ == '__main__':
    root = tk.Tk()

    scrollbar = tk.Scrollbar(root)  # build the scrollbar
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    lb1 = tk.Listbox(root, width = 35, yscrollcommand=scrollbar.set)
    lb2 = tk.Listbox(root, yscrollcommand=scrollbar.set)

    lb1.pack(side="left", fill="x", expand=True)
    lb2.pack(side="left", fill="x", expand=True)

    scrollbar.config(command=lb2.yview)

    for i in range(100):
        lb1.insert(tk.END, str(i))
        lb2.insert(tk.END, str(100 - i))



    print(len(str(4.5)))


    root.mainloop()



