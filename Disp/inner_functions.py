from collections import defaultdict
from typing import Tuple
import re
import file_support as fs
import db_support as ds
import numpy as np
from global_structures import *
import datetime
from numpy.lib import recfunctions as rfn




app = None

stage = 0
internal_storage = None
internal_aggs = None
format_1 = re.compile(r'[^a-zA-Z0-9]')
format_2 = re.compile(r'^\d{8}$|^\d{10}$|^\d{12}$|^\d{14}$')

class NoNewKeysDefaultDict(defaultdict):
    def __missing__(self, key):
        return None
            
    def __setitem__(self, key, value):
        if key not in self:
            return
        super().__setitem__(key, value)

    def add_to_set(self, key, value):
        if key in self:
            self[key].add(value)

class OrderedSet:
    def __init__(self, iterable=None):
        self.items = []
        self.lookup = set()
        if iterable:
            for item in iterable:
                self.add(item)
                
    def add(self, item):
        if item not in self.lookup:
            self.lookup.add(item)
            self.items.append(item)
    
    def remove(self, item):
        if item in self.lookup:
            self.lookup.remove(item)
            self.items.remove(item)
    
    def __contains__(self, item):
        return item in self.lookup
    
    def __iter__(self):
        return iter(self.items)
    
    def __len__(self):
        return len(self.items)
    
    def __repr__(self):
        return f"OrderedSet({self.items})"
    
    def min(self):
        return min(self.items)
    
    def max(self):
        return max(self.items)

def evaluate_uci(s: str) -> str:
    s_str = str(s)
    stem = format_1.sub('', s_str)
    if format_2.match(stem):
        return stem if len(stem) in (8, 10) else stem[4:]
    return '!' + s_str

def split_indexs(column_string:str) -> list:
    return [c.strip() for c in column_string.split(",")]


UCI_PARSE = np.frompyfunc(evaluate_uci,1,1)




def undirected_set(parse:bool, use_filter:bool, output:int, duplication:int, keys:str):

    #Setup Data
    internal = defaultdict(lambda: defaultdict(int))

    #Format
    format = Format(intended_names=["KEY"], search_names=[split_indexs(keys)], intended_types=[object], use_filter=use_filter)
    
    #Iterate Data
    for file in app.iterate_selected_data(format):
        file_id, subfile_id = file.file, file.subfile
        for batch in app.updating_iterating_batches(file=file):
            data = batch.data
            if parse:
                data = UCI_PARSE(data)
            for row in data:
                internal[row[0]][subfile_id] += 1
         
    #Aggregate Data
    aggregates = []
    for value, subfiles in internal.items():
        total_count = sum(subfiles.values())
        total_sub = len(subfiles)

        #Duplication
        if duplication == 0:
            duplicate = total_count > 1
        elif duplication == 1:
            duplicate = total_sub > 1
        elif duplication == 2:
            pass

        #Output
        if (output == 0) or (output == 1 and duplicate) or (output == 2 and not duplicate):
            aggregates.append([value, total_count, ";".join(subfiles.keys())])

    #Report
    fs.create_csv_output(data=aggregates, file_name=app.choose_file_name("UNDIRECTED"), columns=["KEYS","COUNT","VALUES"])
        
def directed_set(parse:bool, use_filter:bool, output:int, keys:str):
    global internal
    global stage

    #Storing
    if stage == 0:
        internal = defaultdict(set)
    else:
        for k in internal:
            internal[k] = set()
        internal = NoNewKeysDefaultDict(set,internal)

    format = Format(intended_names=["KEY"], search_names=[split_indexs(keys)], intended_types=[object], use_filter=use_filter)


    #Filling
    for file in app.iterate_selected_data(format):
        file_id, subfile_id = file.file, file.subfile
        for batch in app.updating_iterating_batches(file=file):
            data = batch.data
   
            if parse:
                data = UCI_PARSE(data)
            if stage == 0:
                for row in data:
                    internal[row[0]].add(subfile_id)
            else:
                for row in data:
                    internal.add_to_set(row[0], subfile_id)
    
    #Aggregating
    if stage == 0:
        pass
    else:
        aggregates = []
        for value, subfiles in internal.items():
            if (len(subfiles) == 0 and output == 0) or (len(subfiles) > 1 and output == 1):
                aggregates.append([value, len(subfiles), ';'.join(subfiles)])

        #REPORT
        fs.create_csv_output(data=aggregates, file_name=app.choose_file_name("DIRECTED"), columns=["KEYS", "COUNT", "VALUES"])
    
    stage ^= 1
       
def match_col(parse:bool, use_filter:bool, output:int, aggregate:int, keys:str, values:str):

    #Storing
    if aggregate in [0,1]:
        internal = defaultdict(list) 
    elif aggregate in [2,3,4]:
        internal = defaultdict(set)
    else:
        pass


    format = Format(intended_names=["KEY", "VALUE"], search_names=[split_indexs(keys), split_indexs(values)], intended_types=[object, object], use_filter=use_filter)


    for file in app.iterate_selected_data(format):
        file_id, subfile_id = file.file, file.subfile
        for batch in app.updating_iterating_batches(file=file):
            data = batch.data

            print(data)

            if parse:
                data[:,0] = UCI_PARSE(data[:,0])

            if aggregate in [0,1]:
                for row in data:
                    internal[row[0]].append(row[1])
            else:
                for row in data:
                    internal[row[0]].add(row[1])

    #Aggregates
    aggregates = []
    for key, values in internal.items():
        total_count = len(values)
        if (output == 0) or (output == 1 and total_count == 1) or (output == 2 and total_count > 1):

            if total_count == 1:
                aggregates.append([key, 1, values[0]])
            elif aggregate in [0,2]:
                print(values)
                aggregates.append([key, total_count, ';'.join(map(str,values))])
            else:
                if aggregate == 1:
                    aggregates.append([key,  total_count, sum(values)])
                elif aggregate == 3:
                    aggregates.append([key, total_count, max(values)])
                elif aggregate == 4:
                    aggregates.append([key, total_count, min(values)])

    fs.create_csv_output(data=aggregates, file_name=app.choose_file_name("MATCH"), columns=["KEY","COUNT","VALUE"])







def upload_triggers(trigger):
    
    intended = [['UCI']]
    if trigger == 0:
        intended.append(['Citizenship_Date'])
    elif trigger == 1:
        intended.append(['Decreased_Date'])
    elif trigger == 2:
        intended.append(['Departure_Date'])
    
    format = Format(intended_names=["UCI", "TRIGGER_DATE"], search_names=intended, intended_types=[np.int32, np.dtype('datetime64[D]')])

    for file in app.iterate_selected_data(format):
        for batch in app.updating_iterating_batches(file=file):
            data = batch.data

            data = np.unique(data, axis=0)
            
            trigger_col = np.full(data.shape[0], trigger)

            data = rfn.append_fields(data, 'TRIGGER', trigger_col, usemask=False)

            data = (convert_row_to_python(row) for row in data)

            ds.upload_triggers(data=data)




def upload_events(clear:bool):
    names = ["id", "UCI", "EVENT_TYPE", "EVENT_DATE", "EVENT_STAGE", "LAST_DATE"]
    format = Format(intended_names=names, search_names=names, 
                    intended_types=[np.int32, np.int32, str, np.dtype('datetime64[D]'), str, np.dtype('datetime64[D]')])

    for file in app.iterate_selected_data(format):
        for batch in app.updating_iterating_batches(file=file):

            data = batch.data
            data = (convert_row_to_python(row) for row in data)

            ds.upload_events(data)












def upload_files(clear:bool):
    
    names = ["UCI", "VOLUMES", "TEMP", "LOCATION", "OFFICE"]
    format = Format(intended_names=names, search_names=names, intended_types=[np.int32, np.int32, str, str, str])


    for file in app.iterate_selected_data(format):
        for batch in app.updating_iterating_batches(file=file):
            data = batch.data

            #data = np.unique(data, axis=0)
            
            #trigger_col = np.full(data.shape[0], trigger)

            #data = rfn.append_fields(data, 'TRIGGER', trigger_col, usemask=False)

            data = (convert_row_to_python(row) for row in data)

            print(data)

            ds.upload_files(data=data)




    


def convert_row_to_python(row):
    return tuple(
        x.item() if isinstance(x, (np.integer, np.floating)) else
        x.astype(datetime.datetime) if isinstance(x, np.datetime64) else
        x
        for x in row
    )