import pandas as pd
import requests
from utils import helper
import chardet


def read_csv(uploaded_file):

    file_name = uploaded_file.name.replace("_"," ").split(" ")

    circulate_no = file_name[1]

    encoding = helper.check_encodings(uploaded_file)

    # df = pd.read_csv(uploaded_file, encoding=encoding, header=0).rename(columns={"Device_ID.": "device_id"})
    df = pd.read_csv(uploaded_file, encoding=encoding, header=0)
    df = df.iloc[3:, :]

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

    try:

        url = "http://10.168.4.51:8000/mssql/get_product_name"
        params = {"circulate_no": circulate_no}  # Query parameters

        response = requests.get(url, params=params)
        product_name = response.text.strip('"')
        if not product_name:
            raise Exception("Product name not found")
    except Exception as e:
        return df, f"{circulate_no},流转单号错误，无法获取产品编码。请检查文件命名规则和流转单号！"

    # The criteria for identifying outliers
    try:
        criteria = helper.criteria[product_name]
    except KeyError:
        return df, f"{product_name} 不需要挑选离散点，请检查文件"

    # Identifying the exact columns with the criteria
    test_cols = []
    for cri in criteria:
        for names in detail_df.columns.tolist():
            if cri in names:
                # print(cri, names)
                test_cols.append(names)
    # print(f'The number of test cols is {len(test_cols)}')

    detail_df = detail_df[test_cols]
    detail_df = detail_df.apply(pd.to_numeric, errors='coerce')



    # 1️⃣ Calculate mean and std for each numeric column
    stats = detail_df.agg(['mean', 'std'])

    # 2️⃣ Compute lower & upper limits
    lower = stats.loc['mean'] - 6 * stats.loc['std']
    upper = stats.loc['mean'] + 6 * stats.loc['std']

    # 3️⃣ Create a boolean mask where any column value is out of range
    mask = (detail_df < lower) | (detail_df > upper)

    # 4️⃣ Combine across all numeric columns (row-wise OR)
    detail_df['outlier_3sigma'] = mask.any(axis=1)

    outlier_df = detail_df[detail_df["outlier_3sigma"] == True]

    outlier = (basic_df.join(outlier_df, how='right')["Device_ID."])

    return outlier, None
