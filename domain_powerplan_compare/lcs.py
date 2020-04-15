"""
lcs.py
~~~~~~~~~~~~~~~~~~~~
This is a random implementation of the longest common sequence problem
"""


memo = {}

def lcs_length(l1: list, l2: list, l1_idx: int, l2_idx: int):
    if (l1_idx, l2_idx) in memo:
        return memo.get(((l1_idx, l2_idx)))
    elif (l1_idx == len(l1)) or (l2_idx == len(l2)):
        return 0
    elif l1[l1_idx] == l2[l2_idx]:
        output = 1 + lcs_length(l1, l2, l1_idx + 1, l2_idx + 1)
        memo[(l1_idx, l2_idx)] = output
        return output
    else:
        return max(
            lcs_length(l1, l2, l1_idx + 1, l2_idx), lcs_length(l1, l2, l1_idx, l2_idx + 1)
            )


def lcs_repr(l1: list, l2: list, l1_idx: int, l2_idx: int):
    if (l1_idx, l2_idx) in memo:
        return memo.get(((l1_idx, l2_idx)))
    elif (l1_idx == len(l1)) or (l2_idx == len(l2)):
        return ''
    elif l1[l1_idx] == l2[l2_idx]:
        output = lcs_repr(l1, l2, l1_idx + 1, l2_idx + 1) + l1[l1_idx]
        memo[(l1_idx, l2_idx)] = output
        return output
    else:
        return max(
            lcs_repr(l1, l2, l1_idx + 1, l2_idx), lcs_repr(l1, l2, l1_idx, l2_idx + 1)
            ) 

def LCS(X, Y):
    m = len(X)
    n = len(Y)
    # An (m+1) times (n+1) matrix
    C = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            if X[i-1] == Y[j-1]: 
                C[i][j] = C[i-1][j-1] + 1
            else:
                C[i][j] = max(C[i][j-1], C[i-1][j])
    return C

def printDiff(C, X, Y, i, j):
    output = []
    if i > 0 and j > 0 and X[i-1] == Y[j-1]:
        output.extend(printDiff(C, X, Y, i-1, j-1))
        output.append(X[i-1])
        
    else:
        if j > 0 and (i == 0 or C[i][j-1] >= C[i-1][j]):
            output.extend(printDiff(C, X, Y, i, j-1))
            output.append("+ " + Y[j-1])
        elif i > 0 and (j == 0 or C[i][j-1] < C[i-1][j]):
            output.extend(printDiff(C, X, Y, i-1, j))
            output.append("- " + X[i-1])

    return output

def diff_wrapper(l1: list, l2: list) -> list:
    output_list = []
    C = LCS(l1, l2)
    return printDiff(C, l1, l2, len(l1), len(l2))

if __name__ == "__main__":
    #print(lcs_length('ABCDGH', 'AEDFHR', 0, 0))

    print(lcs_repr('ABCDGH', 'AEDFHR', 0, 0)[::-1])

    b0783 = ['DUAL MODALITY', 'Link to Protocol: Combined Chemotherapy CISplatin and Radiation Treatment for Locally Advanced Squamous Cell Carcinoma of the Head and Neck', 'Proceed With Treatment Based on Blood Work From', 'OK to Proceed with Treatment', 'Administer oncology treatment on inpatient unit', '               Pre-Chemo Metrics', 'Neutrophil', 'Neutrophils', 'Platelet Count', 'Creatinine Clearance Greater Than or Equal to 60 mL/min within 24 hours', '               Pre-Medications', 'Patient to take own supply of pre-medications. RN/Pharmacist to confirm', 'dexamethasone', 'netupitant-palonosetron 300 mg-0.5 mg cap', 'LORazepam', 'prochlorperazine', 'diphenhydrAMINE', '               Pre-Hydration', 'potassium chloride 20 mmol-magnesium sulfate 2 g/1000 mL D51/2NS bag', '               Treatment Regimen', 'Zero Time', 'Chemotherapy is only to be administered if concurrent with radiation. If there is a significant delay in the delivery of Cycle 2, scheduling with radiation may result in omission of Cycle 3', 'CISplatin-KCL 10 mmol-mannitol 30 g in NS 1000 mL', '               Post-Hydration', 'potassium chloride 20 mmol-magnesium sulfate 2 g/1000 mL D51/2NS bag', ' Additional Orders', 'Any additional orders will be displayed below. Please review and adjust scheduled administration time as needed']
    p0783 = ['DUAL MODALITY', 'Link to Protocol: Combined Chemotherapy CISplatin and Radiation Treatment for Locally Advanced Squamous Cell Carcinoma of the Head and Neck', 'Proceed With Treatment Based on Blood Work From', 'OK to Proceed with Treatment', 'Administer oncology treatment on inpatient unit', '               Pre-Chemo Metrics', 'Neutrophil', 'Neutrophils', 'Platelet Count', 'Creatinine Clearance Greater Than or Equal to 60 mL/min within 24 hours', '               Pre-Medications', 'Patient to take own supply of pre-medications. RN/Pharmacist to confirm', 'ondansetron', 'dexamethasone', 'netupitant-palonosetron 300 mg-0.5 mg cap', 'LORazepam', 'prochlorperazine', 'diphenhydrAMINE', '               Pre-Hydration', 'potassium chloride 20 mmol-magnesium sulfate 2 g/1000 mL D51/2NS bag', '               Treatment Regimen', 'Zero Time', 'Chemotherapy is only to be administered if concurrent with radiation. If there is a significant delay in the delivery of Cycle 2, scheduling with radiation may result in omission of Cycle 3', 'CISplatin-KCL 10 mmol-mannitol 30 g in NS 1000 mL', '               Post-Hydration', 'potassium chloride 20 mmol-magnesium sulfate 2 g/1000 mL D51/2NS bag', '               Additional Orders', 'Any additional orders will be displayed below. Please review and adjust scheduled administration time as needed']    
    # print(lcs_wrapper(b0783, p0783, 0, 0))
    print(printDiff(LCS(b0783, p0783), b0783, p0783, len(b0783), len(p0783)))