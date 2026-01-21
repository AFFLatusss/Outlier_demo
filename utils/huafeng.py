import pandas as pd
from utils import helper


def read_csv(uploaded_file, type="modules"):
    
    encoding = helper.check_encodings(uploaded_file)
    skip = 0
    # with open(uploaded_file,encoding=encoding) as f:
    #     lines = f.readlines()
    #     for rownum, line in enumerate(lines):
    #         if line.startswith("Article_Nr.,Date,Time"):
    #             skip = rownum
    #         elif line.startswith("SITE_NUM,PART_ID,PASSFG,SOFT_BIN"):
    #             # raise Exception("Incorrect data format. Not SPEA-like. Header starts with [SITE_NUM,PART_ID,PASSFG,SOFT_BIN], should be [Article_Nr.,Date,Time]")
    #             return None,  "错误的数据格式！不符合SPEA格式标准。正确表头应该是[Article_Nr.,Date,Time]....等"

        # ❗ FIX 1 — Read lines directly from UploadedFile
    file_bytes = uploaded_file.getvalue()
    text = file_bytes.decode(encoding)
    lines = text.splitlines()

    for rownum, line in enumerate(lines):
        if line.startswith("Article_Nr.,Date,Time"):
            skip = rownum
        elif line.startswith("SITE_NUM,PART_ID,PASSFG,SOFT_BIN"):
            return None, "错误的数据格式！不符合SPEA格式标准。正确表头应该是[Article_Nr.,Date,Time]..."


    file_name = uploaded_file.name.replace("_"," ").split(" ")

    circulate_no = file_name[0]


    # df = pd.read_csv(uploaded_file, encoding=encoding, header=0).rename(columns={"Device_ID.": "device_id"})
    df = pd.read_csv(uploaded_file, encoding=encoding, header=0, skiprows=skip).rename(columns={"Device_ID": "Device_ID."})
    units_df = df.iloc[:3, :]
    df = df.iloc[3:, :]  #Remove unit and UL limit
    df = df[df["PassFail"] == "Pass"] #Remove fail rows

    # positioning the index cols for splitting the DataFrame
    index_cols = []
    for names in df.columns.tolist():
        if "DC_NTC_TEST" in names:
            index_cols.append(names)

    if not index_cols:
       raise ValueError("未找到DC_NTC_TEST列，请检查上传的文件！")
    
    index_pos = df.columns.get_loc(index_cols[-1])

        
    # Splitting the DataFrame
    basic_df = df.iloc[:,:7]
    detail_df = df.iloc[:,index_pos:]


    if type == "modules":
        return helper.calc_outlier(basic_df, detail_df, circulate_no)
    elif type == "graphs":
        return detail_df, units_df.iloc[:, index_pos:]
    