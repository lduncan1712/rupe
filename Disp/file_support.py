from typing import Union, Any, Optional, Iterator
import win32com.client, os, gc, json
from typing import Tuple
from datetime import datetime, date
import csv
import numpy as np
from global_structures import *
import pywintypes




from numpy.typing import NDArray
from dataclasses import dataclass


# ----------------------------------------------


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

def open_subfile(type: str, file: Any, subfile: Any) -> Any:
    if type == "EXCEL":
        subfile = file.Sheets(subfile)
    else:
        raise ValueError ("Invalid Type" + type)
    
    return subfile

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


BATCH_SIZE = 100000


def iterate_sheet(sheet:Any, format:Format) -> File:

    has_table = sheet.listObjects.Count > 0

    if has_table:
        table = sheet.ListObjects(1)
        format.found_names = [c for c in table.HeaderRowRange.Value[0]]
        if format.use_filter:
            used = table.DataBodyRange.SpecialCells(12)
        else:
            used = table.DataBodyRange
    #Iterate Cell Range
    else:
        used = sheet.UsedRange
        format.found_names = list(used.Rows(1).Cells.Value[0])
        used = sheet.Range(sheet.Cells(used.Row + 1, used.Column), 
                           sheet.Cells(used.Row + used.Rows.Count - 1, used.Column + used.Columns.Count - 1))
  

    #Validate Schema
    format.intended_indexs,valid = validate_schema(format=format)

    rows = get_row_counts(type="EXCEL", data=used)

    #Iterate
    if has_table and format.use_filter:
        iterator = iterate_areas(rng=used, format=format)
    else:
        iterator = iterate_range(rng=used, format=format)

    return File(rows=rows, data=iterator, valid=valid)

def iterate_range(rng:Any, format:Format, offset:int = 0) -> Iterator[BatchData]:

    #Size
    n_rows = rng.Rows.Count
    r_first = rng.Row
    c_first = rng.Column
    ws = rng.Worksheet

    #Create Batch Ranges
    for s_off in range(0, n_rows, BATCH_SIZE):
        e_off = min(s_off + BATCH_SIZE - 1, n_rows - 1)
        r_start = s_off + r_first
        r_end = r_first + e_off
        r_totals = r_end - r_start + 1 + offset

        np_columns = []

        #Add Columns
        for col_id, dtype in zip(format.intended_indexs, format.intended_types):
            batch_column = ws.Range(ws.Cells(r_start, c_first+col_id), ws.Cells(r_end, c_first+col_id))
               
            np_columns.append(np.array(batch_column.Value, dtype=dtype).reshape(-1))
    
        #dtype = np.dtype(list(zip(format.intended_names, format.intended_types)))
        #print(dtype)

        data = np.core.records.fromarrays(np_columns, names=format.intended_names)

        valid = validate_data(format=format, data=data, is_excel=True)

        yield BatchData(data=data, rows=r_totals, valid=valid)
        
def iterate_areas(rng:Any, format:Format) -> Iterator[BatchData]:

    #Size
    ws = rng.Worksheet
    r_first = rng.Areas(1).Row
    next_empty = r_first

    for area in rng.Areas:
        offset = area.Row - next_empty
        next_empty = area.Row + area.Rows.Count - 1
        #TODO: Empty Columns In Area Can Be Dropped, Should Flag
        yield from iterate_range(rng=area, format=format, offset=offset)





def iterate_csv(csv:Any, format:Format) -> File:
    
    names = [col.strip().lstrip("\ufeff") for col in csv.readline().strip().split(",")]
    format.intended_indexs, valid = validate_schema(found_names=names, format=format)
    iterator = iterate_rows(csv=csv, format=format)
    rows = get_row_counts(type="CSV", data=csv)
    return File(rows=rows, data=iterator, valid=valid)

def iterate_rows(csv:Any, format:Format) -> Iterator[BatchData]:
    
    rows = []
    r_cumulative = 0

    temp_intended = format.intended_types[0][1] if len(format.intended_types) == 1 else temp_intended

    for line in csv:
        row = line.rstrip("\n").split(",")
        row = [row[i] for i in format.intended_indexs]
        rows.append(row)
        r_cumulative += 1

        if r_cumulative == BATCH_SIZE:
            data = np.array(rows, dtype=temp_intended)
            valid = validate_data(format=format, data=data, is_excel=False)

            yield BatchData(data=data, rows=BATCH_SIZE, valid=valid)
            rows = []
            r_cumulative = 0

    if not r_cumulative == 0:
        data = np.array(rows, dtype=temp_intended)
        valid = validate_data(format=format, data=data, is_excel=False)

        yield BatchData(data=data, rows=r_cumulative, valid=valid)
        rows = []
        r_cumulative = 0



def validate_schema(format:Format) -> Tuple[list[int], bool]:
    kept_indexs = []

    print("INTENDED_NAMES")
    print(format.intended_names)

    print("FOUND NAMES")
    print(format.found_names)

    for group in format.search_names:
        print("LOOKING AT GROUP")
        print(group)
        if len(group) == 1 and group[0].isdigit():
            c = int(group[0])
            if c >= 0 and c < len(format.found_names):
                kept_indexs.append(c)
            else:
                return kept_indexs, False
        else:    
            found_in_group = [format.found_names.index(x) for x in format.found_names if x in group]
            print("Found In Group")
            print(found_in_group)

            if len(found_in_group) == 1:
                kept_indexs.append(found_in_group[0])
            else:
                return kept_indexs, False
    return kept_indexs, True

def validate_data(format:Format, data:NDArray, is_excel:bool=False) -> bool:
    for i, (n,t) in enumerate(zip(format.intended_names, format.intended_types)):
        col_type = data[n].dtype
        intended_type = np.dtype(t)
        match = np.issubdtype(col_type, intended_type)
        if not match:
            #But Its Excel, Its Intended To Be Integer, But Is Actually Floating
            if is_excel and np.issubdtype(intended_type, np.integer) and np.issubdtype(col_type, np.floating):
                print("SHOULD BE TRYING TO CONVERT")
                if np.all(np.modf(data[:,i] == 0)):
                    data[:, i] = data[:,i].astype(np.int32)
                else:
                    return False
            else:
                return False
    return True




def get_row_counts(type:str, data:Any) -> int:
    if type == "EXCEL":
        areas = data.Areas.Count
        if areas > 1:
            r_top = data.Areas(1).Row
            r_bot = data.Areas(areas).Row + data.Areas(areas).Rows.Count - 1
            return r_bot - r_top + 1
        else:
            return data.Rows.Count
    elif type == "CSV":
        rows = sum(1 for _ in data)
        data.seek(0)
        next(data)
        return rows
    else:
        ValueError("Invalid Type Entered")











def create_csv_output(data:Tuple, file_name:str, columns:list) -> None:

    if file_name is None:
        return

    with open(file_name, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(data)                