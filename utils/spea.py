import pandas as pd
from utils import helper
import os
def read_csv(uploaded_file, type="modules"):
    file_name = uploaded_file.name.replace("_"," ").split(" ")
    circulate_no = file_name[0]

    encoding = helper.check_encodings(uploaded_file)
    ext = os.path.splitext(uploaded_file.name)[1].lower()

    if ext == '.csv':
        df = pd.read_csv(uploaded_file, encoding=encoding, header=0)
    elif ext == '.xlsx':
        df = pd.read_excel(uploaded_file, header=0)
    else:
        raise ValueError("不支持的文件格式")

    units_df = df.iloc[:3, :]
    df = df.iloc[3:, :]
    df = df[df["PassFail"] == "Pass"]

    index_cols = [c for c in df.columns if "NTC" in c]
    if not index_cols:
        raise ValueError("未找到NTC列，请检查上传的文件！")

    index_pos = df.columns.get_loc(index_cols[-1])

    ntc_avg = pd.to_numeric(df.iloc[:, index_pos], errors='coerce').mean()
    if ntc_avg <= 4000:
        raise ValueError("未找到常温测试数据，请检查")

    basic_df = df.iloc[:, :7]
    detail_df = df.iloc[:, index_pos:]

    if type == "modules":
        return helper.calc_outlier(basic_df, detail_df, circulate_no)
    elif type == "graphs":
        return detail_df, units_df.iloc[:, index_pos:]
