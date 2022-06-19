#passgen

import random
import tkinter as tk


uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

lowercase = uppercase.lower()

digits = "0123456789"

symbols = "{}[];.,1234%&^*~`+-/|"

upper, lower, nums, syms = True, True, True, True
#change to false as neceessary

all = ""
if upper:
    all += uppercase
if lower:
    all += lowercase
if nums:
    all += digits
if syms:
    all += symbols

length = 15
amount = 5

for x in range(amount):
    password = "".join(random.sample(all, length))
    print(password)


root= tk.Tk()

canvas1 = tk.Canvas(root, width = 300, height = 300)
canvas1.pack()

def clickapp():
    label1 = tk.Label(root, text= password, fg='green', font=('tacoma', 12, 'bold'))
    canvas1.create_window(150, 200, window=label1)


button1 = tk.Button(text='Pass Gen', command=click, bg='red', fg='white')
canvas1.create_window(150, 150, window=button1)

root.mainloop()