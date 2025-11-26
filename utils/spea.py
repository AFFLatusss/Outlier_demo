import pandas as pd
from utils import helper


def read_csv(uploaded_file):

    file_name = uploaded_file.name.replace("_"," ").split(" ")

    circulate_no = file_name[0]

    encoding = helper.check_encodings(uploaded_file)

    # df = pd.read_csv(uploaded_file, encoding=encoding, header=0).rename(columns={"Device_ID.": "device_id"})
    df = pd.read_csv(uploaded_file, encoding=encoding, header=0)
    df = df.iloc[3:, :]  #Remove unit and UL limit
    df = df[df["PassFail"] == "Pass"] #Remove fail rows

    # positioning the index cols for splitting the DataFrame
    index_cols = []
    for names in df.columns.tolist():
        if "NTC" in names:
            index_cols.append(names)

    if not index_cols:
        return df, "未找到NTC列，请检查上传的文件！"
    
    index_pos = df.columns.get_loc(index_cols[-1])


    # check ntc avg
    ntc_avg = pd.to_numeric(df.iloc[:,index_pos], errors='coerce').mean()
    if ntc_avg <= 4000:
        return df, "未找到常温测试数据，请检查"


        
    # Splitting the DataFrame
    basic_df = df.iloc[:,:7]
    detail_df = df.iloc[:,index_pos:]

    return helper.calc_outlier(basic_df, detail_df, circulate_no)