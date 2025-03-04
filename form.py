from typing import Any, Optional
from pathlib import Path
import pandas as pd
import chardet

class Form():
    def __init__(self, file_path: str | Path,
                 index_col: Optional[str] = None):
        self.file_path = Path(file_path)
        self.index_col = index_col
        if not self.file_path.exists():
            raise FileNotFoundError(f"File {file_path} not found")

    def get_col_names(self) -> list[str]:
        return self.df.columns.tolist()

    def set_index_col(self, index_col: str):
        self.index_col = index_col

    def update_data(self, row, col, value: Any):
        try:
            row = self.df.index.get_loc(row)
        except KeyError:
            raise KeyError('The row "%s" is not found.' % row)
        try:
            col = self.df.columns.get_loc(col)
        except KeyError:
            self.df[col] = pd.Series(dtype=type(value))
            col = self.df.columns.get_loc(col)
        self.df.iloc[row, col] = value

    def merge_from(self, form: 'Form', update_col: str) -> int:
        count = 0
        values = {}
        for row in form.df.itertuples():
            values[getattr(row, self.index_col)] = getattr(row, update_col)
        for row in self.df.itertuples():
            if getattr(row, self.index_col) in values:
                self.update_data(row.Index, update_col, values[getattr(row, self.index_col)])
                count += 1
        return count

    def save(self, file_path: str | Path, encoding: Optional[str] = None):
        file_path = Path(file_path)
        if not file_path.parent.exists():
            raise FileNotFoundError(f"Directory {file_path.parent} does not exist")
        if file_path.suffix == '.csv':
            if encoding is None:
                encoding = self.encoding if hasattr(self, 'encoding') else 'gb18030'
            self.df.to_csv(file_path, index=False, encoding=encoding)
        elif file_path.suffix in ('.xlsx', '.xls'):
            if not hasattr(self, 'excel'):
                self.df.to_excel(file_path, index=False)
            else:
                with pd.ExcelWriter(file_path) as writer:
                    for sheet_name in self.excel.sheet_names:
                        if sheet_name == self.sheet_name:
                            self.df.to_excel(writer, sheet_name=sheet_name, index=False)
                        else:
                            pd.read_excel(self.excel, sheet_name=sheet_name).to_excel(
                                writer, sheet_name=sheet_name, index=False)



def _get_encoding(file_path: str | Path, sample_size: int = 1024) -> str:
    with open(file_path, 'rb') as f:
        raw_data = f.read(sample_size)
    result = chardet.detect(raw_data)
    detected_encoding = result.get('encoding', None)
    confidence = result.get('confidence', 0)
    if detected_encoding and confidence > 0.5:
        return detected_encoding
    try_encodings = ['utf-8', 'gb18030', 'gbk', 'utf-16']
    for enc in try_encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                f.read()
            return enc
        except (UnicodeDecodeError, FileNotFoundError):
            continue
    raise ValueError(f"Cannot detect encoding for {file_path}")

class CSVForm(Form):
    def __init__(self, file_path: str | Path,
                       index_col: Optional[str] = None):
        super().__init__(file_path, index_col)
        if not self.file_path.suffix == '.csv':
            raise ValueError("File is not a CSV file")
        self.encoding = _get_encoding(file_path)
        self.df = pd.read_csv(file_path, encoding=self.encoding)

class ExcelForm(Form):
    def __init__(self, file_path: str | Path,
                       index_col: Optional[str] = None,
                       sheet_name: Optional[str] = None,
                       force_load: bool = False):
        super().__init__(file_path, index_col)
        if not self.file_path.suffix in ('.xlsx', '.xls'):
            raise ValueError("File is not an Excel file")
        try:
            self.excel = pd.ExcelFile(file_path)
        except PermissionError:
            raise PermissionError(f"{file_path} is opened in another program, close it and try again")
        if sheet_name is not None:
            self.load_sheet(sheet_name)
        elif force_load:
            self.load_sheet(self.get_sheet_names()[0])

    def get_sheet_names(self):
        return self.excel.sheet_names

    def load_sheet(self, sheet_name: str):
        self.sheet_name = sheet_name
        self.df = pd.read_excel(self.file_path, sheet_name=sheet_name)
