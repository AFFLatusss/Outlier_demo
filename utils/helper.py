import chardet
import requests
import pandas as pd

def check_encodings(uploaded_file):
    # Read the uploaded file bytes directly
    raw_data = uploaded_file.getvalue()
    result = chardet.detect(raw_data)
    encoding = result['encoding']
    return encoding



criteria = {
            "EPG50PIS120E2A-01":["VTH","VCESAT","ICES","IGES","VF", "IR"],
            "LCG50PIS120E1B-3H":["VTH","VCESAT","ICES","IGES","VF", "IR"],
            "EPG75PIS120E2B-01":["VTH","VCESAT","ICES","IGES","VF", "IR"],
            "EPG75PIS120E2A-01":["VTH","VCESAT","ICES","IGES","VF", "IR"],
            "LCG200HB120T7P3-1H":["VTH","VCESAT","ICES","IGES","VF"],
            "LCG150FF120E6E2C-H":["VTH","VCESAT","ICES","IGES","VF"],
            "LCG15FF120E4B1-01":["VTH","VCESAT","ICES","IGES","VF"],
            "LCG35CI120E4B2-02":["VTH","VCESAT","ICES","IGES","VF"],
            "LCG25FF120E4B1-01":["VTH","VCESAT","ICES","IGES","VF"],
            "LCG400HB120E6P2-01":["VTH","VCESAT","ICES","IGES","VF"],
            "LCG450HB120E6P2-01":["VTH","VCESAT","ICES","IGES","VF"],
            "LCG820FF75E7A2-01":["VTH","VCESAT","ICES","IGES","VF"],
            "LCG600FF75E7A2-01":["VTH","VCESAT","ICES","IGES","VF"],
            }

def calc_outlier(basic_df, detail_df, circulate_no):

    

    url = "http://10.168.4.51:8000/mssql/get_product_name"
    params = {"circulate_no": circulate_no}  # Query parameters


    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        product_name = response.text.strip().strip('"')
        if not product_name:
            return None, f"无法找到流转单{circulate_no}对应的产品编码，请检查流转单号和文件命名！"
    except requests.RequestException:
        return None, "无法连接数据库接口，请检查网络或服务器状态！"




    # The criteria for identifying outliers
    test_criteria = criteria.get(product_name)
    if not test_criteria:
        return None, f"{product_name} 不需要挑选离散点，请检查文件！"
    

    # Identifying the exact columns with the criteria
    test_cols = []
    for cri in test_criteria:
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

    outlier = basic_df.loc[outlier_df.index, "Device_ID."]

    return outlier, None
