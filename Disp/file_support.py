from typing import Union, Any
import win32com.client, os, gc, json
from typing import Tuple
from datetime import datetime
import csv
import numpy as np
import global_attributes as ga

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


def iterate_excel_files(selected:dict, filter:bool, intended:list[list[str]], cb=None, batch:int = 10000):
    for excel_key, sheet_keys in selected.items():
        wb = open_file(type="EXCEL", path=ga.file_links[excel_key], app=ga.applications["EXCEL"], read=True)
        for sheet_key in sheet_keys:
            ws = wb.Sheets(ga.sheet_names[sheet_key])

            if ws.listObjects.Count > 0:
                table = ws.ListObjects(1)
                found = validate_file_schema(found=[c for c in table.HeaderRowRange.Value[0]], intended=intended)
                used = table.DataBodyRange
                del table
                if filter:
                    iterater = iterate_excel_areas(indexs=found, areas=used.SpecialCells(12))
                else:
                    iterater = iterate_excel_range(indexs=found, rng=used)
            else:
                used = ws.UsedRange
                found = validate_file_schema(found=list(used.Rows(1).Cells.Value[0]), intended=intended)
                used = ws.Range(ws.Cells(used.Row + 1, used.Column), ws.Cells(used.Row + used.Rows.Count - 1, used.Column + used.Columns.Count - 1))
                iterater = iterate_excel_range(indexs=found, rng=used)

            if found is None:
                cb("Schema In File: " + ga.file_links[excel_key] + "-" + ga.sheet_names[sheet_key] + " Is Wrong Skipping")
                iterater = iterater([0])
                gc.collect()
            
            yield excel_key, sheet_key, iterater
            del used, 
        close_file(type="EXCEL",file=wb)
        del wb
        gc.collect()

def iterate_excel_range(indexs:list[int], rng):

    n_rows = rng.Rows.Count
    r_first = rng.Row
    c_first = rng.Column
    c_last = c_first + rng.Columns.Count - 1
    ws = rng.Worksheet

    yield n_rows

    for s_off in range(0, n_rows, BATCH_SIZE):
        e_off = min(s_off + BATCH_SIZE - 1, n_rows - 1)
        r_start = s_off + r_first
        r_end = r_first + e_off
        r_totals = r_end - r_start + 1

        batch_rng = ws.Range(ws.Cells(r_start, c_first), ws.Cells(r_end, c_last))

        values = clean_file_data(data=np.array(batch_rng.Value, dtype=object), kept=indexs, reverse_marshall=True)
        yield values,  r_totals
        del values, batch_rng, ws

def iterate_excel_areas(indexs:list[int], areas):

    def bound_generator(areas):
        for area in areas.Areas:
            start = area.Row
            end = start + area.Rows.Count - 1
            yield start, end

    ws = areas.Worksheet
    r_first = areas.Areas(1).Row
    a_last = areas.Areas(areas.Areas.Count)
    r_last = a_last.Row + a_last.Rows.Count - 1
    c_first = areas.Areas(1).Column
    c_last = a_last.Column + a_last.Columns.Count - 1

    yield r_last - r_first + 1

    gen = bound_generator(areas)
    s_current, e_current = next(gen)

    for r_start in range(r_first, r_last, BATCH_SIZE):
        r_end  = min(r_start + BATCH_SIZE - 1, r_last)
        rng = ws.Range(ws.Cells(r_start, c_first), ws.Cells(r_end, c_last))
        values = clean_file_data(data=np.array(rng.Value, dtype=object), kept=indexs, reverse_marshall=True)
        n_rows = values.shape[0]
        mask = np.zeros(n_rows, dtype=bool)

        for row in range(r_start, r_end + 1):        
            if row > e_current:
                s_current, e_current = next(gen)
            elif row >= s_current and row <= e_current:
                mask[row - r_start] = 1
                
        values = values[mask]
            
        yield values, r_end - r_start + 1


def iterate_csv_files(selected:list, intended:list[list[str]], cb=None, batch:int = 10000):
    for csv_key in selected:
        csv = open_file(type="CSV", path=ga.file_links[csv_key], app=ga.applications["CSV"], read=True)
        found = validate_file_schema(found=[col.strip().lstrip("\ufeff") for col in csv.readline().strip().split(",")], intended=intended)

        if found is None:
            cb("Schema In File: " + ga.file_links[csv_key] + " Is Wrong Skipping")
            iterater = iter([0])
            gc.collect()
        else:
            iterater = iterate_csv_rows(indexs=found, csv=csv)

        yield csv_key, csv_key, iterater
        close_file(type="CSV", file=csv)
        del csv
        gc.collect()

def iterate_csv_rows(csv, indexs:list[int]):

    rows = []
    r_cumulative = 0
    r_total = sum(1 for _ in csv)
    yield r_total

    csv.seek(0)
    next(csv)

    for line in csv:
        row = line.rstrip("\n").split(",")
        row = [row[i] for i in indexs]
        rows.append(row)
        r_cumulative += 1

        if r_cumulative == BATCH_SIZE:
            yield np.array(rows, dtype=object), BATCH_SIZE
            rows = []
            r_cumulative = 0

    if not r_cumulative == 0:
        yield np.array(rows, dtype=object), r_cumulative
        rows = []
        r_cumulative = 0

# ----------------------------------------------------------------

def validate_file_schema(found:list, intended:list[list[str]]) -> list:
        kept_columns = []

        if all(inner == [""] for inner in intended):
            return np.arange(len(found))

        for column_group in intended:
            columns_found = [found.index(x) for x in found if x in column_group]
            if len(columns_found) != 1:
                return None
            kept_columns.append(columns_found[0])
        return kept_columns

def clean_file_data(data:Any, kept:list[int], reverse_marshall:bool) -> list:
    data = data[:, kept]
    if reverse_marshall:
        mask = np.vectorize(lambda x: isinstance(x, float) and x.is_integer())(data)
        data[mask] = data[mask].astype(int)
    return data

def create_csv_output(data:Tuple, file_name:str, columns:list) -> None:

    if file_name is None:
        return

    with open(file_name, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(data)                