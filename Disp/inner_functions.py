from collections import defaultdict
import global_attributes as ga
from typing import Tuple
import re
import file_support as fs
import db_support as ds
import numpy as np

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


#----------------------------------------------------------
#----------------------------------------------------------
#----------------------------------------------------------


def undirected_set(parse:bool, use_filter:bool, output:int, duplication:int, keys:str):

    #Storing
    internal = defaultdict(lambda: defaultdict(int))

    #Filling
    for file, sheet, data in ga.app.iterate_selected_data(use_filter=filter, 
                                                          intended_names=[split_indexs(keys)],
                                                          intended_types=[('KEY', object)]):
        if parse:
            data = UCI_PARSE(data)
        for row in data:
            internal[row[0]][sheet] += 1

    #Aggregating
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
    fs.create_csv_output(data=aggregates, file_name=ga.app.choose_file_name("UNDIRECTED"), columns=["KEYS","COUNT","VALUES"])
        
def directed_set(parse:bool, filter:bool, output:int, keys:str):
    global internal
    global stage

    #Storing
    if stage == 0:
        internal = defaultdict(set)
    else:
        for k in internal:
            internal[k] = set()
        internal = NoNewKeysDefaultDict(set,internal)

    #Filling
    for file, sheet, data in ga.app.iterate_selected_row_files(filter=filter,intended=[split_indexs(keys)]):
        if parse:
            data = UCI_PARSE(data)
        if stage == 0:
            for row in data:
                internal[row[0]].add(sheet)
        else:
            for row in data:
                internal.add_to_set(row[0], sheet)
    
    #Aggregating
    if stage == 0:
        pass
    else:
        aggregates = []
        for value, subfiles in internal.items():
            if (len(subfiles) == 0 and output == 0) or (len(subfiles) > 1 and output == 1):
                aggregates.append([value, ';'.join(subfiles)])

        #REPORT
        fs.create_csv_output(data=aggregates, file_name=ga.app.choose_file_name("DIRECTED"), columns=["KEYS", "COUNT", "VALUES"])
    
    stage ^= 1
       
def match_col(parse:bool, filter:bool, output:int, aggregate:int, keys:str, values:str):

    #Storing
    if aggregate in [0,1]:
        internal = defaultdict(list) 
    elif aggregate in [2,3,4]:
        internal = defaultdict(set)
    else:
        pass

    #Filling
    for file, sheet, data in ga.app.iterate_selected_row_files(filter=filter, intended=[split_indexs(keys), split_indexs(values)]):
        if parse:
            data[:,0] = UCI_PARSE(data[:,0])
        for row in data:
            internal[row[0]].add(row[1])

    #Aggregates
    aggregates = []
    for key, values in internal.items():
        total_count = len(values)
        if (output == 0) or (output == 1 and total_count == 1) or (output == 2 and total_count > 1):

            if total_count == 1:
                aggregates.append([key, values[0], 1])
            elif aggregate in [0,2]:
                aggregates.append([key, total_count, ';'.join(values)])
            else:
                if aggregate == 1:
                    aggregates.append([key,  total_count, sum(values)])
                elif aggregate == 3:
                    aggregates.append([key, total_count, max(values)])
                elif aggregate == 4:
                    aggregates.append([key, total_count, min(values)])

    fs.create_csv_output(data=aggregates, file_name=ga.app.choose_file_name("MATCH"), columns=["KEY","COUNT","VALUE"])

def upload_triggers(trigger):
    
    intended = [['UCI']]
    if trigger == 0:
        intended.append(['Citizenship_Date'])
    elif trigger == 1:
        intended.append(['Decreased_Date'])
    elif trigger == 2:
        intended.append(['Departure_Date'])

    for _, _, data in ga.app.iterate_selected_data(filter=False, intended_names=intended,
                                                        dtype=[
                                                            ()
                                                        ]):


        data[:, 1] = np.array([np.datetime64(d) for d in data[:, 1]])
        data = np.unique(data, axis=0)
        data = np.insert(data, data.shape[1], trigger, axis=1)
        ds.upload_triggers(data=fs.numpy_to_tuple(data))