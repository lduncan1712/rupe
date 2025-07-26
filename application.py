import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Callable

# === Sample data ===
FUNCTIONS: Dict[str, List[str]] = {
    'Math': ['Add', 'Subtract'],
    'String': ['Concatenate', 'Split'],
}

FUNCTION_DETAILS: Dict[str, Dict[str, List[str] or str]] = {
    'Add': {
        'description': 'Adds two numbers together.',
        'fields': ['Number 1', 'Number 2'],
        'checkboxes': ['Round result']
    },
    'Split': {
        'description': 'Splits a string by delimiter.',
        'fields': ['Input String', 'Delimiter'],
        'checkboxes': ['Trim spaces']
    }
}

current_lang = "EN"

def toggle_language() -> None:
    global current_lang
    current_lang = "FR" if current_lang == "EN" else "EN"
    btn_toggle_lang.config(text=f"Language: {current_lang}")

def run_function() -> None:
    progress.start(10)
    root.after(2000, progress.stop)  # Simulate a task delay

# === Function Tree View ===
def create_left_tree(parent: tk.Widget, callback: Callable[[ttk.Treeview], None]) -> ttk.Treeview:
    tree = ttk.Treeview(parent)
    for group, funcs in FUNCTIONS.items():
        parent_id = tree.insert('', 'end', text=group, open=True)
        for func in funcs:
            tree.insert(parent_id, 'end', text=func)
    tree.pack(fill='both', expand=True)
    tree.bind('<<TreeviewSelect>>', lambda e: callback(tree))
    return tree

# === File Tree View ===
def create_file_tree(parent: tk.Widget) -> None:
    tree = ttk.Treeview(parent)
    root_node = tree.insert('', 'end', text='Root', open=True)
    f1 = tree.insert(root_node, 'end', text='Folder1', open=True)
    tree.insert(f1, 'end', text='data.txt')
    tree.insert(f1, 'end', text='image.png')
    f2 = tree.insert(root_node, 'end', text='Scripts')
    tree.insert(f2, 'end', text='script.py')
    tree.pack(fill='both', expand=True)

# === Populate Middle Panel Tabs ===
def populate_tabs(func_name: str) -> None:
    for widget in options_tab.winfo_children():
        widget.destroy()
    for widget in summary_tab.winfo_children():
        widget.destroy()

    detail = FUNCTION_DETAILS.get(func_name)
    if not detail:
        tk.Label(options_tab, text="No options for this function").pack()
        tk.Label(summary_tab, text="No summary available").pack()
        return

    # -- OPTIONS TAB --
    tk.Label(options_tab, text="Options", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=10, pady=5)

    for field in detail.get('fields', []):
        tk.Label(options_tab, text=field).pack(anchor="w", padx=10)
        tk.Entry(options_tab).pack(fill="x", padx=10, pady=2)

    for option in detail.get('checkboxes', []):
        var = tk.BooleanVar()
        tk.Checkbutton(options_tab, text=option, variable=var).pack(anchor="w", padx=10)

    # -- SUMMARY TAB --
    tk.Label(summary_tab, text="Function Summary", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=10, pady=5)
    tk.Label(summary_tab, text=detail['description'], wraplength=400, justify="left").pack(anchor="w", padx=10)

# === Function Selection Callback ===
def on_function_selected(tree: ttk.Treeview) -> None:
    selected = tree.selection()
    if not selected:
        return
    item_text = tree.item(selected[0], "text")
    populate_tabs(item_text)

# === Main App ===
root = tk.Tk()
root.title("Function UI with Tabs")
root.geometry("1200x600")

# --- Panels ---
left_frame = tk.Frame(root, width=300, bg="#f0f0f0")
middle_frame = tk.Frame(root, width=500, bg="#ffffff")
right_frame = tk.Frame(root, width=300, bg="#f7f7f7")

left_frame.pack(side="left", fill="both", expand=True)
middle_frame.pack(side="left", fill="both", expand=True)
right_frame.pack(side="left", fill="both", expand=True)

# --- Tree on the Left ---
create_left_tree(left_frame, on_function_selected)

# --- File Tree on the Right ---
create_file_tree(right_frame)

# --- Bottom Buttons in Right Panel ---
button_frame = tk.Frame(right_frame)
button_frame.pack(side='bottom', fill='x', pady=10, padx=10)

btn_add = tk.Button(button_frame, text="Add File")
btn_add.pack(side="left", padx=(0, 5))

btn_remove = tk.Button(button_frame, text="Remove File")
btn_remove.pack(side="right", padx=(5, 0))

# --- Middle Panel with Notebook ---
notebook = ttk.Notebook(middle_frame)
options_tab = tk.Frame(notebook)
summary_tab = tk.Frame(notebook)

notebook.add(options_tab, text="Options")
notebook.add(summary_tab, text="Summary")
notebook.pack(fill="both", expand=True)

# --- Bottom of Middle Panel: Run Button + Progress Bar ---
middle_bottom_frame = tk.Frame(middle_frame)
middle_bottom_frame.pack(side='bottom', fill='x', pady=10, padx=10)

btn_run = tk.Button(middle_bottom_frame, text="Run", command=run_function)
btn_run.pack(side="left", padx=5)

progress = ttk.Progressbar(middle_bottom_frame, orient="horizontal", mode="indeterminate", length=150)
progress.pack(side="left", padx=5)

# --- Bottom of Left Panel: Language Toggle ---
left_bottom_frame = tk.Frame(left_frame)
left_bottom_frame.pack(side='bottom', fill='x', pady=10, padx=10)

btn_toggle_lang = tk.Button(left_bottom_frame, text="Language: EN", command=toggle_language)
btn_toggle_lang.pack(side="left", padx=5)

# Start main loop
root.mainloop()


