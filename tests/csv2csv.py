import sys
sys.path.append('.')

from form import CSVForm

sour = CSVForm('csv_example/from.csv', index_col='学号')
dest = CSVForm('csv_example/to.csv', index_col='学号')

dest.merge_from(sour, update_col='政治面貌')
dest.save('csv_example/result.csv')
