# Merge Forms

[Chinese README](README_zh.md)

## Introduction
* Worried about the scene below?
  ![1664683369356](image/README/1664683369356.png)
* Welcome to try this project, merge the data in `from.csv` to `to.csv`, and achieve the following effect.
  ![1664683411461](image/README/1664683411461.png)
* Support format: from and to both support csv/xlsx/xls format.

## Usage
* Install dependencies
  ```shell
  pip install -r requirements.txt
  ```
* Run
  ```shell
  python ui.py
  ```
* Take the above example as an example, enter the information.
  ![1664718425633](image/README/1664718425633.png)
* You can set default value in `config.json`, for example:
  ```json
  {
    "from": "./example/from.xlsx",
    "to": "./example/to.xlsx",
    "fromsheet": "Sheet1",
    "tosheet": "Sheet1",
    "baserow": "姓名",
    "updatecol": "是否党员",
    "savename": "./example/result.xlsx"
  }
  ```

* The project has not been strictly tested. If there is any problem, submit issues.