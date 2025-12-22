def calculate_listening_band(score_percentage):
    """
    Convert percentage score to IELTS band (approximate conversion)
    """
    if score_percentage >= 95:
        return 9.0
    elif score_percentage >= 88:
        return 8.5
    elif score_percentage >= 82:
        return 8.0
    elif score_percentage >= 76:
        return 7.5
    elif score_percentage >= 70:
        return 7.0
    elif score_percentage >= 64:
        return 6.5
    elif score_percentage >= 58:
        return 6.0
    elif score_percentage >= 52:
        return 5.5
    elif score_percentage >= 46:
        return 5.0
    elif score_percentage >= 40:
        return 4.5
    elif score_percentage >= 34:
        return 4.0
    elif score_percentage >= 28:
        return 3.5
    elif score_percentage >= 22:
        return 3.0
    elif score_percentage >= 16:
        return 2.5
    elif score_percentage >= 10:
        return 2.0
    else:
        return 1.0