from tkinter import *
import os
master = Tk()

def var_states():
    for g in GRAMMARS:
        print(g, GRAMMARS[g].get())
#    print("male: %d,\nfemale: %d" % (var1.get(), var2.get()))

def refresh_grammar_list(m):
    grammars = {}
    # row = 0
    for row, filename in enumerate(os.listdir('grammars')):
        filename = filename.split('.')[0]
        print(filename)
        newvar = IntVar()
        grammars[filename] = newvar
        Checkbutton(m, text=filename, variable=newvar).grid(row=row, sticky=W)
        # Checkbutton(m, text=filename, variable=newvar).pack(fill=X)
        # row += 1
    return grammars

Label(master, text="Your sex:").grid(row=0, sticky=W)
GRAMMARS = refresh_grammar_list(master)

# Checkbutton(master, text="male", variable=var1).grid(row=1, sticky=W)
# Checkbutton(master, text="female", variable=var2).grid(row=2, sticky=W)
Button(master, text='Quit', command=master.quit).grid(row=len(GRAMMARS)+1, sticky=W, pady=4)
Button(master, text='Show', command=var_states).grid(row=len(GRAMMARS)+2, sticky=W, pady=4)
mainloop()