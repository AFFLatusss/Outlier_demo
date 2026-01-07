import pandas as pd
from utils import helper


def read_csv(uploaded_file, type="modules"):

    file_name = uploaded_file.name.replace("_"," ").split(" ")

    circulate_no = file_name[1]

    encoding = helper.check_encodings(uploaded_file)

    # df = pd.read_csv(uploaded_file, encoding=encoding, header=0).rename(columns={"Device_ID.": "device_id"})
    try:
        df = pd.read_csv(uploaded_file, encoding=encoding, header=0)
    except Exception as e:
        return None, f"错误的数据格式！不符合FT-003格式标准。请检查文件"
    
    units_df = df.iloc[:3, :]
    df = df.iloc[3:, :]  #Remove unit and UL limit
    df = df[df["PassFail"] == "Pass"] #Remove fail rows

    # positioning the index cols for splitting the DataFrame
    index_cols = []
    for names in df.columns.tolist():
        if "NTC_1mA" in names:
            index_cols.append(names)

    if not index_cols:
        return df, "未找到NTC_1mA列，请检查上传的文件！"
    
    index_pos = df.columns.get_loc(index_cols[-1])
    # print(f'the last NTC_1mA column is at position {index_pos}')

        
    # Splitting the DataFrame
    basic_df = df.iloc[:,:7]
    detail_df = df.iloc[:,index_pos:]

    if type == "modules":
        return helper.calc_outlier(basic_df, detail_df, circulate_no)
    elif type == "graphs":
        return detail_df, units_df.iloc[:, index_pos:]

