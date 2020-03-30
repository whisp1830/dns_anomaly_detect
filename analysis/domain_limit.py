def calculate_traffic_limit(limit, daily_history, hourly_history):
    pre_limit = limit
    now_limit = 0
    if daily_history:
        now_limit = round(pre_limit * 0.09 + daily_history[-1]["traffic"] * 0.01)
    elif hourly_history:
        now_limit = round(pre_limit * 0.95 + hourly_history[-1]["traffic"] * 0.05)
    if now_limit < 10 :
        now_limit = 10
    return now_limit