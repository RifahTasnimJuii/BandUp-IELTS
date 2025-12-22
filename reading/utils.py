def reading_band_score(correct):
    """
    IELTS Academic Reading (approx)
    """
    if correct >= 39:
        return 9.0
    elif correct >= 37:
        return 8.5
    elif correct >= 35:
        return 8.0
    elif correct >= 33:
        return 7.5
    elif correct >= 30:
        return 7.0
    elif correct >= 27:
        return 6.5
    elif correct >= 23:
        return 6.0
    elif correct >= 19:
        return 5.5
    elif correct >= 15:
        return 5.0
    elif correct >= 13:
        return 4.5
    else:
        return 4.0
