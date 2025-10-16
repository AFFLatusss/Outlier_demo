import chardet

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
            "LCG35CI120E4B2-02":["VTH","VCESAT","ICES","IGES","VF"],
            "LCG400HB120E6P2-01":["VTH","VCESAT","ICES","IGES","VF"],
            "LCG450HB120E6P2-01":["VTH","VCESAT","ICES","IGES","VF"],
            "LCG820FF75E7A2-01":["VTH","VCESAT","ICES","IGES","VF"],
            "LCG600FF75E7A2-01":["VTH","VCESAT","ICES","IGES","VF"],
            }
