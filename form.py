# -*- encoding: utf-8 -*-
import pandas as pd
import chardet

def getEncodeing(filename):
    with open(filename, 'rb') as f:
        return chardet.detect(f.read())['encoding']

class Form(object):
    def __init__(self, filename: str, base_col=None, sheet_name=0, **kwargs):
        """
        Form(filename: str, base_col=None, sheet_name=0, **kwargs) -> None.
        @param:
            filename: str, the file path
            base_col: int|str, find based on which column
            sheet_name: int|str, the sheet name (only for excel)
        """
        if not (filename.endswith('.csv') \
            or filename.endswith('.xlsx') \
            or filename.endswith('.xls')):
                raise ValueError('The file type is not supported.')
        self.filename = filename
        self.type = 0 if filename.endswith('.csv') else 1
        if self.type == 0:
            self.data = pd.read_csv(filename, index_col=base_col, encoding=getEncodeing(filename), **kwargs)
        else:
            self.data = pd.read_excel(filename, index_col=base_col, sheet_name=sheet_name, **kwargs)

    def update_data(self, row, col, value:any):
        """
        update_data(row, col, value:any) -> None.
        @param:
            row, the row index
            col, the column index
            value: any, the value to be updated
        """
        try:
            row = self.data.index.get_loc(row)
        except KeyError:
            raise KeyError('The row "%s" is not found.' % row)
        try:
            col = self.data.columns.get_loc(col)
        except KeyError:
            self.data[col] = ''
            col = self.data.columns.get_loc(col)
        self.data.iloc[row, col] = value

    def merge_from(self, form:'Form', update_col) -> int:
        """
        merge_from(form:'Form', update_col:str) -> int.
        @param:
            form: 'Form', the form where the data is updated from
            update_col: the column to be updated
        @return:
            the number of updated items
        """
        no = []
        count = 0
        for row in form.data.index:
            if row in self.data.index:
                self.update_data(row, update_col, form.data.loc[row, update_col])
                count += 1
            else:
                no.append(row)
        return count

    def save(self, outfile: str, encode:str = None):
        """
        save(outfile: str) -> None.
        @param:
            outfile: str, the file path to be saved
        """
        if outfile.endswith('.csv'):
            if encode is None:
                encode = getEncodeing(self.filename) if self.type == 0 else 'gb2312'
            self.data.to_csv(outfile, encoding=encode)
        elif outfile.endswith('.xlsx') or outfile.endswith('.xls'):
            self.data.to_excel(outfile)
        else:
            raise ValueError('The file type is not supported.')