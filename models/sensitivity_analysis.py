from models.dcf_model import calculate_dcf, project_fcf

def generate_sensitivity_matrix(base_fcf, shares, growth_rate, wacc_range, terminal_growth_range):
    """
    Returns a matrix (dictionary) of intrinsic values based on WACC and terminal growth combos.
    """
    matrix = {}
    projected_fcf = project_fcf(base_fcf, growth_rate)

    for wacc in wacc_range:
        row = []
        for tg in terminal_growth_range:
            try:
                result = calculate_dcf(projected_fcf, wacc, tg, shares)
                row.append(round(result['intrinsic_value'], 2))
            except ZeroDivisionError:
                row.append(None)  # Handle WACC = TG case
        matrix[round(wacc * 100, 1)] = row  # Use WACC% as row key
    return matrix
