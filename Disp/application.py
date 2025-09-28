import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import copy

from global_structures import *


from TEMP_CheckboxTreeView import CheckboxTreeview
#from ttkwidgets import CheckboxTreeview


from typing import Any, List, Callable
import gc
import file_support as fs
import db_support as ds
import inner_functions 
from inner_functions import *




keys = ['FOLDER', 'EXCEL', 'WORD', 'PDF', 'CSV', 'EXCEL-SHEET']
file_keys = ['EXCEL','WORD','PDF', 'CSV']
app = None

class FunctionApp:

    def __init__(self, root: tk.Tk) -> None:    
        self.root = root
        self.item_counts =   {k: 0 for k in keys}
        self.select_counts = {k: 0 for k in keys}
        self.item_set =   {k: set() for k in keys}
        self.select_set = {k: set() for k in keys}

        self.applications = {key: fs.open_application(key) for key in file_keys}
        self.file_links =      {}
        self.sheet_links =     {}
        self.sheet_names =     {}

        self.text =          {}
        self.node_counter =    0
        self.total_label =     None
        self.select_label =    None
        self.progress =        None
        self.options_tab =     None
        self.description_tab = None
        self.db =              None
        self.dropdowns =       {}
        self.fields =          {}
        self.checkboxes =      {}

        self.setup_settings()
        self.setup_frames()

    def setup_settings(self) -> None:
        try:
            settings_data = fs.open_file(type="JSON", path="settings.json", app=None, read=False)
            self.imported_paths = settings_data["paths"]
            self.text = fs.open_file(type="JSON",path=settings_data["language"],app=None, read=False)
            self.db = settings_data["database"]
        except Exception as e:
            self.show_message(str(e))
            self.root.destroy()

    def setup_frames(self) -> None:
        
        self.left_frame = tk.Frame(self.root, width=200, bg="#f0f0f0")
        self.middle_frame = tk.Frame(self.root, width=200, bg="#f0f0f0")
        self.right_frame = tk.Frame(self.root, width=300, bg="#f0f0f0")
        self.left_frame.pack(side="left", fill="both", expand=False)
        self.middle_frame.pack(side="left", fill="both", expand=False)
        self.right_frame.pack(side="left", fill="both", expand=True)
        
        self.middle_frame.pack_propagate(False)

        self.setup_left_tree()
        self.setup_middle_tabs()
        self.setup_right_tree()

    def setup_left_tree(self) -> None:
        self.left_tree = ttk.Treeview(self.left_frame)
        self.left_tree.pack(fill='both', expand=True)
        self.left_tree.bind('<<TreeviewSelect>>', lambda e: self.populate_tabs())
        self.btn_frame = tk.Frame(self.left_frame)
        self.btn_frame.pack(side='bottom', fill='x', pady=10, padx=10)

        parent_id = self.left_tree.insert('', 'end', text='//', open=True)
        for func_key, func_data in self.text["functions"].items():
            self.left_tree.insert(parent_id, 'end', text=func_data["name"], open=False, tags=func_key)

        #'parent_id = self.left_tree.insert('', 'end', text="**", open=True)
        #'for func_key, func_data in self.text["database_functions"].items():
        #''    self.left_tree.insert(parent_id, 'end', text=func_data["name"], open=False, tags=func_key)


        self.db_label = ttk.Label(self.left_frame, text="Storage:")
        self.db_label.pack(fill="x",padx=10, pady=(5,0))
        self.db_dropdown = ttk.Combobox(self.left_frame, values = self.db, state="readonly")

        def on_db_change(event=None):
            db = self.db_dropdown.get()
            if not db: return
            setup = ds.connect_to_db(db)
            if not setup:
                self.db_dropdown.set("")
        
        self.db_dropdown.bind("<<ComboboxSelected>>", on_db_change)
        self.db_dropdown.pack(fill="x", padx=10, pady=(0,10))

    def setup_middle_tabs(self) -> None:
        notebook = ttk.Notebook(self.middle_frame)
        self.options_tab = tk.Frame(notebook)
        self.summary_tab = tk.Frame(notebook)
        notebook.add(self.options_tab, text="Options")
        notebook.add(self.summary_tab, text="Description")
        notebook.pack(fill="both", expand=True)
        bottom = tk.Frame(self.middle_frame)
        bottom.pack(side='bottom', fill='x', pady=10, padx=10)

        top_row = tk.Frame(bottom)
        top_row.pack(side="top", fill="x", pady=(0,5))  

        run_button = tk.Button(top_row, text=self.text["run_button"], command=self.run_function)
        run_button.pack(side="left", padx=5)

        self.progress_label = tk.Label(top_row, text="...")
        self.progress_label.pack(side="left", padx=5)

        # Progress bar below
        self.progress = ttk.Progressbar(bottom, orient="horizontal", length=150, mode="determinate")
        self.progress.pack(side="top", fill="x")  # fill horizontal width
        

        #self.progress = ttk.Progressbar(bottom, orient="horizontal", length=150, mode="determinate")
        #self.progress.pack(side="left", padx=5)
        #run_button = tk.Button(bottom, text=self.text["run_button"], command=self.run_function).pack(side="left", padx=5)
        #self.progress_label = tk.Label(bottom, text="...")
        #self.progress_label.pack(side="left", padx=5)

    def setup_right_tree(self) -> None:

        tree_container = tk.Frame(self.right_frame)
        tree_container.pack(fill="both", expand=True)


        vsb = ttk.Scrollbar(tree_container, orient='vertical')
        vsb.pack(side='right', fill='y')
        hsb = ttk.Scrollbar(tree_container, orient='horizontal')
        hsb.pack(side='bottom', fill='x')
        self.right_tree = CheckboxTreeview(tree_container, show='tree', yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # self.right_tree.grid(row=0, column=0, sticky="nsew")
        # vsb.grid(row=0, column=1, sticky="ns")
        # hsb.grid(row=1, column=0, sticky="ew")

        # # let the tree grow inside the container
        # tree_container.rowconfigure(0, weight=1)
        # tree_container.columnconfigure(0, weight=1)

        vsb.config(command=self.right_tree.yview)
        hsb.config(command=self.right_tree.xview)

        self.right_tree.pack(fill='both', expand=True)

        #self.right_tree.column("#0", width=400, stretch=False)

        #self.right_tree.column("#0", width=400, stretch=False)



        self.right_tree.tag_configure('FOLDER', foreground='#C8B69F', font=('Arial',10, 'italic'))
        self.right_tree.tag_configure('WORD', foreground='blue', font=('Arial', 10, 'bold'))
        self.right_tree.tag_configure('PDF', foreground='red', font=('Arial', 10, 'bold'))
        self.right_tree.tag_configure('EXCEL', foreground='#006400', font=('Arial', 10, 'bold'))
        self.right_tree.tag_configure('CSV', foreground='black', font=('Arial',10, 'bold'))
        self.right_tree.tag_configure('EXCEL-SHEET', foreground='#228B22', font=('Arial', 10, 'italic'))
        button_frame = tk.Frame(self.right_frame)
        button_frame.pack(side='bottom', fill='x', pady=10, padx=10)
        tk.Button(button_frame, text=self.text["add_button"], command=self.add_items).pack(side="left", padx=5)
        tk.Button(button_frame, text=self.text["remove_button"], command=self.remove_items).pack(side="left", padx=5)
        tk.Button(button_frame, text=self.text["open_button"], command=self.open_node).pack(side="left", padx=5)

        def on_check(event=None):
            checked_items = set(self.right_tree.get_checked())
            for key in keys:
                self.select_set[key] = self.item_set[key] & checked_items
                self.select_counts[key] = len(self.select_set[key])
            self.update_counts()

        self.right_tree.bind('<<CheckboxTreeviewCheckChanged>>', on_check)
        self.right_tree.bind('<ButtonRelease-1>', lambda e: self.root.after(50, on_check))
     
        self.root_node = self.right_tree.insert('', 'end', text='Root', tags=("FOLDER",), open=True)
        for path in self.imported_paths:
            node = self.get_or_create_node(path=path, tag=fs.determine_type(path), parent=self.root_node,  fullPath=path)
        self.imported_paths.clear()

        info_frame = tk.Frame(self.right_frame)
        info_frame.pack(side='bottom', fill='x', pady=5, padx=10)
        self.total_label = tk.Label(info_frame, text="-")
        self.select_label = tk.Label(info_frame, text="-")
        self.total_label.pack(side='left', padx=(0, 20))
        self.select_label.pack(side='left')

        self.update_counts()
    
    def populate_tabs(self) -> None:
        for widget in self.options_tab.winfo_children():
            widget.destroy()
        for widget in self.summary_tab.winfo_children():
            widget.destroy()   

        selected = self.left_tree.selection()
        if not selected: return
        func_name = self.left_tree.item(selected[0], "tags")
        if not func_name: return

        detail = self.text["functions"][func_name[0]]  

        self.dropdowns.clear()
        self.fields.clear()
        self.checkboxes.clear()

        for label, choices in detail.get('dropdowns', {}).items():
            tk.Label(self.options_tab, text=label).pack(anchor="w", padx=10,pady=10)
            var = tk.StringVar()
            var.set(choices[0])
            menu = tk.OptionMenu(self.options_tab, var, *choices)
            menu.var = var
            menu.pack(fill="x", padx=10, pady=2)
            self.dropdowns[label] = (var, choices)
        for field in detail.get('fields', []):
            tk.Label(self.options_tab, text=field).pack(anchor="w", padx=10)
            var = tk.Entry(self.options_tab)
            var.pack(fill="x", padx=10, pady=10)
            self.fields[field] = var
        for option in detail.get('checkboxes', []):
            var = tk.BooleanVar()
            tk.Checkbutton(self.options_tab, text=option, variable=var).pack(anchor="w", padx=10, pady=1)
            self.checkboxes[option] = var

        tk.Label(self.summary_tab, text=detail["description"], wraplength=400, justify="left").pack(anchor="w", padx=10)

    def update_counts(self) -> None:
        items_str = ", ".join(str(v) for v in self.item_counts.values())
        selects_str = ", ".join(str(v) for v in self.select_counts.values())
        self.total_label.config(text=str(items_str))
        self.select_label.config(text=str(selects_str))
        self.total_label.update_idletasks()
        self.select_label.update_idletasks()
        
    def show_message(self, message: str) -> None:
        messagebox.showinfo("Information", message, parent=self.root)

    #----------------------------------------------------------------
    #----------------------------------------------------------------
    #----------------------------------------------------------------

    def get_or_create_node(self, path:str, tag:str, parent:str, fullPath:str) -> str:
        parts = path.replace("\\","/").split("/")
        length = len(parts)
        for index, part in enumerate(parts):
            found = False
            is_last = (index == length - 1)
            for child in self.right_tree.get_children(parent):
                child_item = self.right_tree.item(child)
                if child_item["text"] == part:
                    found = True
                    parent = child
                    break
            if not found: 
                parent = self.create_node(name=part, tag=tag if is_last else "FOLDER", parent=parent, fullPath=fullPath) 
        return parent
    
    def add_parellel_nodes(self, root:str, paths:List) -> None:
        length_paths = len(paths)
        if length_paths > 0:
            tag = fs.determine_type(paths[0])
            node = self.get_or_create_node(paths[0],tag=fs.determine_type(paths[0]) ,parent=root, fullPath=paths[0])
        if length_paths > 1:
            existing_children = {self.right_tree.get_children(self.right_tree.parent(node))}
            for name in paths:
                base_name = fs.get_basename(name)
                if not base_name in existing_children:
                    tag = fs.determine_type(base_name)
                    c = self.create_node(name=base_name, tag=tag, parent=root, fullPath=name)

    def add_cascade_nodes(self, root:str, path:str) -> None:
        for item in fs.iterate_dir(path):
            type = fs.determine_type(path=item.name)
            if item.is_file() and not type is None:
                n = self.create_node(item.name, tag=type, parent=root, fullPath=item.path)
            elif item.is_dir():
                n = self.create_node(item.name, tag="FOLDER", parent=root, fullPath=item.path)
                self.add_cascade_nodes(root=n, path=item.path)
            else:
                print(item)
                self.show_message(message="Unknown Object Within Folder")

    def create_node(self, name:str, tag:str, parent:str, fullPath:str) -> str:
        n = self.right_tree.insert(parent, 'end', iid=self.get_next_node_id(), text=name, tags=(tag,), open=True)
        self.item_counts[tag] += 1
        self.item_set[tag].add(n)
        if tag in file_keys:
            self.file_links[n] = fullPath
        if tag == "EXCEL":
            self.create_subnodes(path=fullPath, tag="EXCEL", parent=n)
        return n
    
    def create_subnodes(self, path:str, tag:str, parent:Any) -> None:
        file = fs.open_file(type=tag, path=path, app=self.applications[tag], read=True)
        subitems = fs.get_subfiles(type=tag, file=file)
        for item in subitems:
            n = self.create_node(name=item, tag='EXCEL-SHEET', parent=parent, fullPath=path)
            self.sheet_links[n] = parent
            self.sheet_names[n] = item
        fs.close_file(type=tag, file=file)
        del file

    def remove_node(self, node:str, up:bool, remove_self:bool) -> None:
        if up:
            while node:
                parent = self.right_tree.parent(node)
                if len(self.right_tree.get_children(parent)) > 1 or parent == self.root_node:
                    break
                else:
                    node = parent

        for child in self.right_tree.get_children(node):
            self.remove_node(child, False,True)
        if remove_self:
            tag = self.right_tree.item(node, "tags")
            self.item_counts[tag[0]] -= 1
            self.item_set[tag[0]].remove(node)
            self.right_tree.delete(node)
            if tag in file_keys:
                self.file_links.pop(node)
            elif tag == "EXCEL-SHEET":
                self.sheet_links.pop(node)
                self.sheet_names.pop(node)
    
    def get_next_node_id(self):
        self.node_counter += 1
        return self.node_counter

    def get_selected_type(self, type:str):
        if type == "EXCEL":
            selected_ids = {}
            for selected_sheet in self.select_set['EXCEL-SHEET']:
                file = self.sheet_links[selected_sheet]
                if file in selected_ids:
                    selected_ids[file].append(selected_sheet)
                else:
                    selected_ids[file] = [selected_sheet]
            return selected_ids
        else:
            return self.select_set[type]

    #-----------------------------------------------------------------
    #-----------------------------------------------------------------
    #-----------------------------------------------------------------
    def add_items(self):
        is_selectionFolder = messagebox.askyesno('', self.text["choice_label"])
        if is_selectionFolder:
            paths = self.select_file_or_folder('FOLDER')
            tag = "FOLDER"
            #REMOVE ALL WITHIN, GET FRESH
            folderNode = self.get_or_create_node(paths,tag=tag,parent=self.root_node, fullPath=paths)
            self.remove_node(node=folderNode, up=False, remove_self=True) #TODO: Bug, Removed Visible Checkbox
            folderNode = self.get_or_create_node(paths,tag=tag,parent=self.root_node, fullPath=paths)
            self.add_cascade_nodes(root=folderNode, path=paths)
        else:
            paths = self.select_file_or_folder('FILE')
            paths = [path for path in paths if not fs.determine_type(paths[0]) is None]
            self.add_parellel_nodes(root=self.root_node, paths=paths)
        self.update_counts()

    def remove_items(self):
        selected = self.right_tree.focus()
        if selected and selected != self.root_node:
            self.remove_node(selected, up=True, remove_self=True)
            self.update_counts()

    def open_node(self):
        selected = self.right_tree.focus()
        if selected and selected != self.root_node and not selected in self.item_set["EXCEL-SHEET"]:
            type = self.right_tree.item(selected, 'tags')
            parts = []
            while selected and selected != self.root_node:
                parts.insert(0, self.right_tree.item(selected, 'text'))
                selected = self.right_tree.parent(selected)
            fullPath = '/'.join(parts)
            fs.open_file_generic(fullPath)

    def on_closing(self):
        for key in file_keys:
            app = self.applications.pop(key, None)
            fs.close_application(type=key, app=app)
            del app
        gc.collect()
        self.applications = None
        root.destroy()
        ds.close_connection()

    def select_file_or_folder(self, mode: str) -> List:
        if mode == 'FILE':
            new_paths = filedialog.askopenfilenames(title= "(*) Select File(s)")
        elif mode == 'FOLDER':
            new_paths = filedialog.askdirectory(title="(*) Select Folder")
        else:
            raise ValueError("Invalid Mode Chosen, Choose Between 'FILE', 'FOLDER'")
        return new_paths
    
    def choose_file_name(self, default:str) -> str:

        path = filedialog.asksaveasfilename(
            title="Save Report (CSV)",
            defaultextension = ".csv",
            initialfile=default,
            filetypes=[("CSV", "*.csv"), ("All Files", "*.*")]
        )

        if not path:
            self.show_message("No Location Selected. Bruhh")
            return None
        else:
            return path

    #-----------------------------------------------------------------
    #-----------------------------------------------------------------
    #-----------------------------------------------------------------





    def run_function(self):
        selected = self.left_tree.selection()
        if not selected: return
        function_key = self.left_tree.item(selected[0], "tags")[0]
        
        dropdown_values =     [choices.index(var.get()) for label, (var, choices) in self.dropdowns.items()]
        field_values =        [entry.get() for field, entry in self.fields.items()]
        checkbox_states =     [var.get() for option, var in self.checkboxes.items()]
        combined_paramaters = [*checkbox_states, *dropdown_values, *field_values]
        self.files_to_run =   0
        self.files_run =      0
        self.rows_to_run =    0
        self.rows_run =       0

        self.progress["value"] = 0
        self.update_label(text="...")
        globals()[function_key](*combined_paramaters)
        self.progress["value"] = 100
        self.update_label(text="Complete")   

    def start_file_progress(self, total:int):
        self.files_run += 1
        self.rows_run = 0
        self.rows_to_run = total
        self.progress["value"] = 5 + 90*((self.files_run - 1)/self.files_to_run)
        self.update_label(text="R: 0/" + str(total))        

    def update_file_progress(self, n:int):
        self.rows_run += n
        self.progress["value"] = 5 + 90*(  ((self.files_run - 1)/self.files_to_run)  + (self.rows_run/self.rows_to_run)/self.files_to_run)
        self.update_label(text="R:" + str(self.rows_run) + " / " + str(self.rows_to_run))
        print("After Updating Progress")
        print(self.progress["value"])
        
    def update_label(self, text:str):
        self.progress_label.config(text=text)
        self.progress_label.update_idletasks()

    def show_file_message(self, file:File, text:str):

        file_name = self.file_links[file.file]
        sub_name = (self.sheet_names[file.subfile] if file.subfile in self.sheet_names else "")

        self.show_message("Selected File: " + file_name + "-" + sub_name + "  " + text)

    def updating_iterating_batches(self, file:File) -> Iterator[BatchData]:


        if not file.valid:
            self.show_file_message(file=file, text="Has Invalid Format. Skipping")
            self.start_file_progress(total=0)
        else:
            self.start_file_progress(total=file.rows)
            for batch in file.data:
                if not batch.valid:
                    self.show_message(file=file, text="Data Doesnt Match Expected Types. Skipping Remainder Of File")
                    break
                else:
                    self.update_file_progress(n=batch.rows)
                    yield batch


    #---------------------------------------------------------------
    #---------------------------------------------------------------
    #---------------------------------------------------------------



    def iterate_selected_data(self, format:Format) -> Iterator[File]:

        self.files_to_run = self.select_counts["EXCEL-SHEET"] + self.select_counts["CSV"]

        excel_keys = self.get_selected_type(type="EXCEL") 
        csv_keys = self.get_selected_type(type="CSV")
        
        #Iterate Excel Files
        for excel_key, sheet_keys in excel_keys.items():
            wb = fs.open_file(type="EXCEL", path=self.file_links[excel_key], app=self.applications["EXCEL"], read=True)
            for sheet_key in sheet_keys:
                ws = fs.open_subfile(type="EXCEL", file=wb, subfile=self.sheet_names[sheet_key])

                file = fs.iterate_sheet(sheet=ws, format=copy.deepcopy(format))
                
                yield File(data=file.data, rows=file.rows, valid=file.valid, file=excel_key, subfile=sheet_key)
                del ws
            fs.close_file(type="EXCEL", file=wb)

        #Iterate CSV Files:
        for csv_key in csv_keys:
            csv = fs.open_file(type="CSV", path=self.file_links[csv_key], app=self.applications["CSV"], read=True)
            file = fs.iterate_csv(csv=csv, format=copy.deepcopy(format))
        
            yield File(data=file.data, rows=file.rows, valid=file.valid, file=csv_key, subfile=csv_key)
            fs.close_file(type="CSV",file=csv)



    def iterate_selected_files_data(self, use_filter:bool, intended_names:list[list[str]], intended_types:list[tuple[str, type]]):
        
        self.files_to_run = self.select_counts["EXCEL-SHEET"] + self.select_counts["CSV"]

        for fileStream in fs.iterate_files_data(excel_keys=self.get_selected_type(type="EXCEL"),
                                                csv_keys=self.get_selected_type(type="CSV"),
                                                intended_names=intended_names,
                                                intended_types=intended_types,
                                                use_filter=use_filter):
            
            if not fileStream.valid:
                self.show_message("Selected File: " + self.file_links[fileStream.file] + "-" + (self.sheet_names[fileStream.subfile] if fileStream.subfile in self.sheet_names else "") + " Doesnt Match Format. Skipping")
                self.start_file_progress(total=0)
            else:
                self.start_file_progress(total=fileStream.total)

                for batch in fileStream.batches:

                    if not batch.valid:
                        self.show_message("Selected File: " + self.file_links[fileStream.file] + "-" + (self.sheet_names[fileStream.subfile] if fileStream.subfile in self.sheet_names else "") + " Data Doesnt Match Expected Types. Skipping Remainder Of File")
                        break
                    else:
                        self.update_file_progress(n=batch.size)
                        yield fileStream.file, fileStream.subfile, batch.data

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x600")

    app = FunctionApp(root)
    inner_functions.app = app
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()