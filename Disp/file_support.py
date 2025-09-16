from typing import Union, Any, Optional
import win32com.client, os, gc, json
from typing import Tuple
from datetime import datetime, date
import csv
import numpy as np
import global_attributes as ga
import pywintypes

def is_valid_file(path:str) -> bool:
    return os.path.isfile(path)

def is_valid_folder(path: str) -> bool:
     return os.path.isdir(path)

def get_basename(path:str) -> str:
    return os.path.basename(path)

def iterate_dir(path:str) -> str:
    return os.scandir(path)

def determine_type(path: str) -> str:

    if is_valid_folder(path):
        return "FOLDER"
    path = os.path.abspath(path)

    if "~" in path:
        return None

    ext = os.path.splitext(path)[1].lower()

    if ext in ['.doc', '.docx', '.dotx']:
        return "WORD"
    elif ext in ['.xls', '.xlsx', '.xlsm']:
        return "EXCEL"
    elif ext in ['.csv']:
        return "CSV"
    elif ext == '.pdf':
        return "PDF"
    else:
        return None
    
#----------------------------------------------------------

def open_application(type: str) -> Any:
    if type == "WORD":
        app = win32com.client.Dispatch("Word.Application")
        app.Visible = False
    elif type == "EXCEL":
        app = win32com.client.DispatchEx("Excel.Application")
        app.Visible = False
        app.DisplayAlerts = False
        app.ScreenUpdating = False
        app.EnableEvents = False
        app.Calculation - -4135
        app.DisplayStatusBar = False
        app.CutCopyMode = False
        app.AutomationSecurity = 3

    elif type == "PDF" or type == "CSV":
        app = None
    else:
        raise ValueError("Invalid Type")

    return app

def open_file(type: str, path: str, app: Any, read: bool) -> Any:
    if type == "WORD":
        file = app.Documents.Open(
                path,
                ReadOnly=read,
                AddToRecentFiles=False,
                ConfirmConversions=False,
                Visible=False
        )
    elif type == "EXCEL":
        file = app.Workbooks.Open(
                path,
                ReadOnly=read,
                UpdateLinks=False,
                AddToMru=False,
                IgnoreReadOnlyRecommended=True,
                Notify=False,
                CorruptLoad=0,  #2 IF NOT TABLE
                Local=True
        )
    elif type == "PDF":
        ... #
    elif type == "JSON":
        file = json.load(open(path, encoding="utf-8"))
    elif type == "CSV":
        file = open(path, 'r', encoding="utf-8")
    else:
        raise ValueError("Invalid Type" + type)
    return file  

def open_file_generic(path:str):
     os.startfile(path)

def get_subfiles(type:str, file:Any) -> list:
    if type == "EXCEL":
        subfiles = [ws.Name for ws in file.Worksheets]
        gc.collect()
    else:
        subfiles = None

    return subfiles
    
def close_file(type: str, file: Any) -> None:
    if type == "WORD": 
        file.Close(SaveChanges=False)
    elif type == "EXCEL":
        file.Close(SaveChanges=False)
    elif type == "PDF":
        ... #TODO
    elif type == "CSV":
        file.close()
    else:
        raise ValueError("Invalid Type")
    del file
    gc.collect()

def close_application(type: str, app: Any) -> None:
    if type == "WORD": 
        app.Quit()
    elif type == "EXCEL":
        app.Quit()
    elif type == "PDF":
        ... #TODO
    elif type == "CSV":
        ...
    else:
        raise ValueError("Invalid Type: " + type)
    del app
    gc.collect()
#--------------------------------------------------------


BATCH_SIZE = 10000


def iterate_selected_files(excel_keys:dict, csv_keys:list, intended_names:list[list[str]], intended_types:list, use_filter: bool = False):

    for excel_key, sheet_keys in excel_keys.items():
        excel_name = ga.file_links[excel_key]
        wb = open_file(type="EXCEL", path=excel_name, app=ga.applications["EXCEL"], read=True)

        for sheet_key in sheet_keys:
            sheet_name = ga.sheet_names[sheet_key]
            ws = wb.Sheets(sheet_name)
            yield excel_key, sheet_key, iterate_excel_sheet(ws=ws, intended_names=intended_names, intended_types=intended_types, use_filter=use_filter)
        del ws
        close_file(type="EXCEL", file=wb)
        del wb
        gc.collect()

    for csv_key in csv_keys:
        csv_name = ga.file_links[csv_key]
        csv = open_file(type="CSV", path=csv_name, app=ga.applications["CSV"], read=True)

        yield csv_key, csv_key, iterate_csv_rows

def iterate_excel_sheet(ws:Any, intended_names:list[list[str]], intended_types:list, use_filter: bool = False):
    print("ITERATING SHEET")
    if ws.listObjects.Count > 0:
        table = ws.ListObjects(1)
        found_names = [c for c in table.HeaderRowRange.Value[0]]
        column_indexs = enforce_file_schema(found_names=found_names, intended_names=intended_names)
        used = table.DataBodyRange
        del table
        if use_filter:
            iterater = iterate_excel_areas(column_indexs=column_indexs, intended_types=intended_types, areas=used.SpecialCells(12))
        else:
            iterater = iterate_excel_range(column_indexs=column_indexs, intended_types=intended_types, rng=used)
    else:
        used = ws.UsedRange
        found_names = list(used.Rows(1).Cells.Value[0])
        column_indexs = enforce_file_schema(found_names=found_names, intended_names=intended_names)
        used = ws.Range(ws.Cells(used.Row + 1, used.Column), ws.Cells(used.Row + used.Rows.Count - 1, used.Column + used.Columns.Count - 1))
        iterater = iterate_excel_range(column_indexs=column_indexs, intended_types=intended_types, rng=used)

    if column_indexs is None:
        print("NONE 12")
        iterator = None

    yield from iterater
    del used
    gc.collect()




def enforce_file_schema(found_names:list, intended_names:list[list[str]]) -> Optional[list[int]]:

    if intended_names == [] or any(inner == [""] for inner in intended_names):
        return None
    
    kept_indexs = []

    for group in intended_names:
        if len(group) == 1 and group[0].isdigit():
            c = int(group[0])
            if c >= 0 and c < len(found_names):
                kept_indexs.append(c)
            else:
                return None
        else:    
            found_in_group = [found_names.index(x) for x in found_names if x in group]
            if len(found_in_group) == 1:
                kept_indexs.append(found_in_group[0])
            else:
                return None
    return kept_indexs

def enforce_data_extraction(intended_types:list, data:Any, use_excel: bool = False):
    
    for i, (name,t) in enumerate(intended_types):
        col_type = data[:, i].dtype
        match = np.issubdtype(col_type, np.dtype(t))
        if not match:
            if use_excel and np.dtype(t) == np.int32:
                if np.issubdtype(col_type, np.floating):
                    if np.all(np.modf(data[:,i] == 0)):
                        data[:, i] = data[:,i].astype(np.int32)
                        continue
            print("NONE 13")
            return None
    return data

def iterate_excel_range(column_indexs:list[int], intended_types:list, rng:range):

    print("ITERATING RANGE:" + rng.Address)

    #Get The Bounds
    n_rows = rng.Rows.Count
    r_first = rng.Row
    c_first = rng.Column
    c_last = c_first + rng.Columns.Count - 1
    ws = rng.Worksheet

    #Return Size
    yield n_rows

    #Create Batch Ranges
    for s_off in range(0, n_rows, BATCH_SIZE):
        e_off = min(s_off + BATCH_SIZE - 1, n_rows - 1)
        r_start = s_off + r_first
        r_end = r_first + e_off
        r_totals = r_end - r_start + 1

        np_columns = []

        #Join Columns
        for col_id, (name, dtype) in zip(column_indexs, intended_types):
            print(dtype)
            batch_column = ws.Range(ws.Cells(r_start, c_first+col_id), ws.Cells(r_end, c_first+col_id))
            np_columns.append(np.array(batch_column.Value, dtype=dtype).reshape(-1))

        #Validate Values
        values = enforce_data_extraction(intended_types=intended_types, data=np.column_stack(np_columns), use_excel=True)
        
        yield values, r_totals
        del values, ws

def iterate_excel_areas(column_indexs:list[int], intended_types:list, areas:range):

    ws = areas.Worksheet
    r_first = areas.Areas(1).Row
    a_last = areas.Areas(areas.Areas.Count)
    r_last = a_last.Row + a_last.Rows.Count - 1
    c_first = areas.Areas(1).Column
    c_last = a_last.Column + a_last.Columns.Count - 1

    yield r_last - r_first + 1

    for area in areas.Areas:
        iter = iterate_excel_range(column_indexs=column_indexs, intended_types=intended_types, rng=area)
        next(iter)
        yield from iter

def iterate_csv_file(csv, intended_names:list[list[str]], intended_types:list):


    found_names = [col.strip().lstrip("\ufeff") for col in csv.readline().strip().split(",")]

    column_indexs = enforce_file_schema(found_names=found_names, intended_names=intended_names)

    iterater = iterate_csv_rows(csv=csv, column_indexs=column_indexs, intended_types=intended_types)

    if column_indexs is None:
        iterater = None

    yield from iterater

def iterate_csv_rows(csv, column_indexs:list[int], intended_types:list):

    rows = []
    r_cumulative = 0
    r_total = sum(1 for _ in csv)
    yield r_total

    csv.seek(0)
    next(csv)

    for line in csv:
        row = line.rstrip("\n").split(",")
        row = [row[i] for i in column_indexs]
        rows.append(row)
        r_cumulative += 1

        if r_cumulative == BATCH_SIZE:
            yield enforce_data_extraction(intended_types=intended_types, data=np.array(rows, dtypes=intended_types), use_excel=False), BATCH_SIZE
            rows = []
            r_cumulative = 0

    if not r_cumulative == 0:
        yield enforce_data_extraction(intended_types=intended_types, data=np.array(rows, dtype=intended_types), use_excel=False), r_cumulative
        rows = []
        r_cumulative = 0






def create_csv_output(data:Tuple, file_name:str, columns:list) -> None:

    if file_name is None:
        return

    with open(file_name, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(data)                