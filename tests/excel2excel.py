import sys
sys.path.append('.')

from form import ExcelForm

sour = ExcelForm('excel_example/from.xlsx', index_col='学号', force_load=True)
dest = ExcelForm('excel_example/to.xlsx', index_col='学号')

print(dest.get_sheet_names())
dest.load_sheet(dest.get_sheet_names()[0])

dest.merge_from(sour, update_col='政治面貌')
dest.save('excel_example/result.xlsx')
