import gc
import copy
import tkinter as tk
import file_support as fs
import db_support as ds

from tkinter import ttk, filedialog, messagebox
from collections import defaultdict
from global_structures import *

from TEMP_CheckboxTreeView import CheckboxTreeview    #ORIGINAL: from ttkwidgets import CheckboxTreeview
from typing import Any, List, Callable, Union

import inner_functions 
from inner_functions import *






















all_keys =  ['FOLDER', 'EXCEL', 'WORD', 'PDF', 'CSV', 'EXCEL-SHEET']
file_keys = ['EXCEL','WORD','PDF', 'CSV']
app =       None

class FunctionApp:
    """Application To Handle Various File, And Database Operations"""

    def __init__(self, root: tk.Tk) -> None:  
        """Initializes Application"""  

        self.root = root
        self.db = None
        self.applications = {key: fs.open_application(key) for key in file_keys}

        self.item_counts =   {k: 0 for k in all_keys}
        self.select_counts = {k: 0 for k in all_keys}
        self.item_set =      {k: set() for k in all_keys}
        self.select_set =    {k: set() for k in all_keys}
        self.counter = 0

        self.file_links =  {}
        self.sheet_links = {}
        self.sheet_names = {}
        self.text_names =  {}

        self.item_label  =     None
        self.select_label =    None
        self.progress_bar =    None
        self.options_tab =     None
        self.description_tab = None
        self.dropdowns =       {}
        self.fields =          {}
        self.checkboxes =      {}

        self.setup_settings()
        self.setup_frames()

    def setup_settings(self) -> None:
        """Imports Required Settings And Text"""

        try:
            settings_data = fs.open_file(type="JSON", path="settings.json", app=None, read=False)

            self.imported_paths = settings_data["paths"]
            self.text =           fs.open_file(type="JSON", path=settings_data["language"], app=None, read=False)
            self.db =             settings_data["database"]
        except FileNotFoundError:
            self.show_message("File Not Found")
            self.root.destroy()
        except KeyError as e:
            self.show_message("Missing Key In File: {e}")
            self.root.destroy()
        except Exception as e:
            self.show_message("Unknown Error: {e}")
            self.root.destroy()

    def setup_frames(self) -> None:
        """Sets Subframes Within Application"""
        
        self.left_frame =   tk.Frame(self.root, width=200, bg="#f0f0f0")
        self.middle_frame = tk.Frame(self.root, width=200, bg="#f0f0f0")
        self.right_frame =  tk.Frame(self.root, width=500, bg="#f0f0f0")

        self.left_frame.pack(side="left", fill="both", expand=False)
        self.middle_frame.pack(side="left", fill="both", expand=False)
        self.right_frame.pack(side="left", fill="both", expand=True)
        self.middle_frame.pack_propagate(False)

        self.setup_left()
        self.setup_middle()
        self.setup_right()

    def setup_left(self) -> None:
        """Sets Left Frame Storing Operation Names And Database Selection"""

        self.left_tree = ttk.Treeview(self.left_frame)
        self.left_tree.pack(fill='both', expand=True)
        self.left_tree.bind('<<TreeviewSelect>>', lambda e: self.populate_tabs())

        parent_id = self.left_tree.insert('', 'end', text='//', open=True)
        for func_key, func_data in self.text["functions"].items():
            self.left_tree.insert(parent_id, 'end', text=func_data["name"], open=False, tags=func_key)

        self.btn_frame = tk.Frame(self.left_frame)
        self.btn_frame.pack(side='bottom', fill='x', pady=10, padx=10)

        self.db_label = ttk.Label(self.left_frame, text="Storage:")
        self.db_label.pack(fill="x",padx=10, pady=(5,0))

        self.db_dropdown = ttk.Combobox(self.left_frame, values = self.db, state="readonly")
        self.db_dropdown.pack(fill="x", padx=10, pady=(0,10))
        self.db_dropdown.bind("<<ComboboxSelected>>", lambda e: ds.connect_to_db(self.db_dropdown.get()) or self.db_dropdown.set(""))

    def setup_middle(self) -> None:
        """Sets Middle Frame Storing Operation Attributes And Operation Progress"""
    
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

        self.progress = ttk.Progressbar(bottom, orient="horizontal", length=150, mode="determinate")
        self.progress.pack(side="top", fill="x") 

    def setup_right(self) -> None:
        """Sets Right Frame Containing File Tree And File Summary Info"""

        tree_container = tk.Frame(self.right_frame)
        tree_container.pack(fill="both", expand=True)
        vsb = ttk.Scrollbar(tree_container, orient='vertical')
        vsb.pack(side='right', fill='y')
        self.right_tree = CheckboxTreeview(tree_container, show='tree', yscrollcommand=vsb.set)
        vsb.config(command=self.right_tree.yview)
        self.right_tree.pack(fill='both', expand=True)

        self.right_tree.tag_configure('FOLDER',      foreground='#C8B69F', font=('Arial',10, 'italic'))
        self.right_tree.tag_configure('WORD',        foreground='blue', font=('Arial', 10, 'bold'))
        self.right_tree.tag_configure('PDF',         foreground='red', font=('Arial', 10, 'bold'))
        self.right_tree.tag_configure('EXCEL',       foreground='#006400', font=('Arial', 10, 'bold'))
        self.right_tree.tag_configure('CSV',         foreground='black', font=('Arial',10, 'bold'))
        self.right_tree.tag_configure('EXCEL-SHEET', foreground='#228B22', font=('Arial', 10, 'italic'))

        button_frame = tk.Frame(self.right_frame)
        button_frame.pack(side='bottom', fill='x', pady=10, padx=10)
        tk.Button(button_frame, text=self.text["add_button"], command=self.add_items).pack(side="left", padx=5)
        tk.Button(button_frame, text=self.text["remove_button"], command=self.remove_items).pack(side="left", padx=5)
        tk.Button(button_frame, text=self.text["open_button"], command=self.open_node).pack(side="left", padx=5)

        def on_check(event=None):
            checked_items = set(self.right_tree.get_checked())
            for key in all_keys:
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
        self.total_label.pack(side='left', padx=(0, 20))

        self.select_label = tk.Label(info_frame, text="-")
        self.select_label.pack(side='left')

        self.update_counts()
    
    def populate_tabs(self) -> None:
        """Fills Middle Tab With The Contents Of Currently Selected Function"""

        for tab in (self.options_tab, self.summary_tab):
            for widget in tab.winfo_children():
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
        """Updates Visual Selection In Right Tree"""

        self.total_label.config(text=", ".join(map(str, self.item_counts.values())))
        self.select_label.config(text=", ".join(map(str, self.select_counts.values())))
        self.total_label.update_idletasks()
                
    def show_message(self, message: str) -> None:
        """Displays Custom Information"""

        messagebox.showinfo("Information", message, parent=self.root)

    #----------------------------------------------------------------
    #----------------------------------------------------------------
    #----------------------------------------------------------------

    def get_or_create_node(self, path:str, tag:str, parent_id:str, fullPath:str) -> str:
        """Returns Node Corrasponding To Path In Right Tree, Creating Missing Nodes"""

        parts = path.replace("\\","/").split("/")
        length = len(parts)
        for index, part in enumerate(parts):
            is_last = (index == length - 1)
            children = {self.right_tree.item(c)["text"]: c for c in self.right_tree.get_children(parent_id)}
            if part in children:
                parent = children[part]
            else:
                parent = self.create_node(name=part, tag=tag if is_last else "FOLDER", parent=parent, fullPath=fullPath) 
        return parent
    
    def add_parellel_nodes(self, root:str, paths:List) -> None:
        """Adds Sibling Nodes From Common Stem"""

        length_paths = len(paths)

        if length_paths > 0:
            first = paths[0]
            tag = fs.determine_type(first)
            node = self.get_or_create_node(paths[0],tag=fs.determine_type(first) ,parent=root, fullPath=first)
        
        if length_paths > 1:
            existing_children = {self.right_tree.get_children(self.right_tree.parent(node))}
            for name in paths:
                base = fs.get_basename(name)
                if not base in existing_children:
                    c = self.create_node(name=base, tag=fs.determine_type(base), parent=root, fullPath=name)

    def add_cascade_nodes(self, root:str, path:str) -> None:
        """Insert A Set Of Nested Files And Folders"""

        for item in fs.iterate_dir(path):
            item_name = item.name
            item_path = item.path

            if item.is_file():
                item_type  = fs.determine_type(path=item_name)
                if item_type is None: continue
                self.create_node(item_name, tag=type, parent=root, fullPath=item_path)
            elif item.is_dir():
                n = self.create_node(item_name, tag="FOLDER", parent=root, fullPath=item_path)
                self.add_cascade_nodes(root=n, path=item_path)
            else:
                self.show_message(message="Unknown Object Within Folder:" + item_path + "Skipping")

    def create_node(self, name:str, tag:str, parent:str, fullPath:str) -> str:
        """Inserts Individual Node Corrasponding To Folder Or File Into Right Tree"""

        n = self.right_tree.insert(parent, 'end', iid=self.get_next_id(), text=name, tags=(tag,), open=True)

        self.item_counts[tag] += 1
        self.item_set[tag].add(n)
        
        if tag in file_keys:
            self.file_links[n] = fullPath

        if tag == "EXCEL": 
            self.create_subnodes(path=fullPath, tag="EXCEL", parent=n)

        return n
    
    def create_subnodes(self, path:str, tag:str, parent:Any) -> None:
        """Creates A Node Corrasponding To Subfile Into Right Tree"""

        try:
            file = fs.open_file(type=tag, path=path, app=self.applications[tag], read=True)
            subitems = fs.get_subfiles(type=tag, file=file)

            for item in subitems:
                n = self.create_node(name=item, tag='EXCEL-SHEET', parent=parent, fullPath=path)
                self.sheet_links[n] = parent
                self.sheet_names[n] = item
        except:
            self.show_message(f"Error Adding SubFiles Of {path}")

        finally:
             fs.close_file(type=tag, file=file)
        
    def remove_node(self, node:str, up:bool, remove_self:bool) -> None:
        """Removes A Node From Right Tree"""

        if up:
            while node:
                parent = self.right_tree.parent(node)
                if len(self.right_tree.get_children(parent)) > 1 or parent == self.root_node:
                    break
                node = parent

        for child in self.right_tree.get_children(node):
            self.remove_node(child, False,True)

        if remove_self:
            tag = self.right_tree.item(node, "tags")[0]

            self.item_counts[tag] -= 1
            self.item_set[tag].remove(node)

            self.right_tree.delete(node)

            self.file_links.pop(node, None)
            self.sheet_links.pop(node, None)
            self.sheet_names.pop(node, None)
    
    def get_next_id(self) -> int:
        """Obtains The Next Unique Node For Right Tree"""
        self.counter += 1
        return self.counter

    def get_selected_type(self, type:str) -> Union[dict, set]:
        """Obtains The Ids Of Selected Nodes Of Specified Type"""
        if type == "EXCEL":
            selected_ids = defaultdict(list)

            for sheet_id in self.select_set['EXCEL-SHEET']:
                selected_ids[self.sheet_links[sheet_id]].append(sheet_id)

            return dict(selected_ids)  
        
        else:
            return self.select_set[type]

    #-----------------------------------------------------------------
    #-----------------------------------------------------------------
    #-----------------------------------------------------------------

    def update_progress(self, progress:int = None, subprogress:int = None, label:str = None, new_subprogress:bool = False):
        """Handles Visual Task Progression For Absolute And Incremental Updates"""
    
        #Set Using Absolue Value And Label        
        if not label is None :
            self.progress_label.config(text:=label)
            self.progress_bar["value"] = progress
        else:
            #Iterating New File
            if new_subprogress:
                self.files_run += 1
                self.rows_run = 0
                self.rows_to_run = subprogress
                self.progress_bar["value"] = 5 + 70*((self.files_run - 1)/self.files_to_run)
                self.progress_label.config(text:="0/" + self.rows_to_run)

            #Iterating Data In File
            else:
                self.rows_run += subprogress
                self.progress_label.config(text:=self.rows_run + "/" + self.rows_to_run)

    def run_function(self):
        """Runs The Currently Selected Function"""

        selected = self.left_tree.selection()
        if not selected: return
        function_key = self.left_tree.item(selected[0], "tags")[0]
        
        dropdown_values =     [choices.index(var.get()) for label, (var, choices) in self.dropdowns.items()]
        field_values =        [entry.get() for field, entry in self.fields.items()]
        checkbox_states =     [var.get() for option, var in self.checkboxes.items()]

        self.update_progress(progress:=0, label:="...")

        globals()[function_key](*[*checkbox_states, *dropdown_values, *field_values])

        self.update_progress(progress:=100, label:="Complete")



    def add_items(self):
        """Adds Files And Folders Into Right Tree"""

        self.update_progress(progress:=10, label:="Adding...")

        is_folder = messagebox.askyesno('', self.text["choice_label"])
        paths = self.select_file_or_folder('FOLDER' if is_folder else 'FILE')

        if is_folder:
            folderNode = self.get_or_create_node(paths,tag="FOLDER",parent=self.root_node, fullPath=paths)
            self.remove_node(node=folderNode, up=False, remove_self=False) 
            #folderNode = self.get_or_create_node(paths,tag=tag,parent=self.root_node, fullPath=paths)  #BUG FIX
            self.add_cascade_nodes(root=folderNode, path=paths)

        else:
            paths = [path for path in paths if not fs.determine_type(paths[0]) is None]
            self.add_parellel_nodes(root=self.root_node, paths=paths)

        self.update_counts()
        self.update_progress(progress:=100, label:="Upload Complete")


    def remove_items(self):
        "Removes Selected Files And Folders"

        selected = self.right_tree.focus()

        if selected and selected != self.root_node:
            self.remove_node(selected, up=True, remove_self=True)
            self.update_counts()

    def open_node(self):
        """Opens Selected Node"""

        selected = self.right_tree.focus()

        if selected and selected != self.root_node: return
        
        if selected in self.item_set["EXCEL-SHEET"]:
            selected = self.right_tree.parent(selected)

        parts = []
        while selected and selected != self.root_node:
            parts.insert(0, self.right_tree.item(selected, 'text'))
            selected = self.right_tree.parent(selected)

        fs.open_file_generic('/'.join(parts))

    def on_closing(self):
        "Procedure Upon Close"

        for key in file_keys:
            fs.close_application(type=key, app=self.applications.pop(key, None))
        
        gc.collect()
        self.applications = None
        root.destroy()
        ds.close_connection()

    def select_file_or_folder(self, mode: str) -> List:
        """Opens File Dialog Allowing Users To Select Files Or Folder"""

        if mode == 'FILE':
            return filedialog.askopenfilenames(title= "(*) Select File(s)")
        elif mode == 'FOLDER':
            return filedialog.askdirectory(title="(*) Select Folder")
        else:
            raise ValueError("Invalid Mode Chosen, Choose Between 'FILE', 'FOLDER'")
    
    def choose_file_name(self, default:str) -> str:
        """Opens A Dialog For Saving A File"""

        path = filedialog.asksaveasfilename(
            title="Save Report (CSV)",
            defaultextension = ".csv",
            initialfile=default,
            filetypes=[("CSV", "*.csv"), ("All Files", "*.*")]
        )

        if path: return path

        self.show_message("No Location Selected. Bruhh")
        return None
        
    #-----------------------------------------------------------------
    #-----------------------------------------------------------------
    #-----------------------------------------------------------------

    
        
        









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
    root.geometry("900x600")

    app = FunctionApp(root)
    inner_functions.app = app
    
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()