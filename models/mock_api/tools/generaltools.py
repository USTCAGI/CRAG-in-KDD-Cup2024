import datetime
import pytz
import re

def parse_datetime(datetime_str):
    # 移除末尾的时区标识 "PT" 和它前面的空格
    datetime_str = datetime_str.replace(' PT', '')
    
    # 定义日期时间的格式
    date_format = "%m/%d/%Y, %H:%M:%S"

    # 使用strptime解析日期时间字符串
    dt = datetime.datetime.strptime(datetime_str, date_format)

    # 由于原始字符串包含时区 "PT"，我们可以将其解析为太平洋时区
    pacific_timezone = pytz.timezone('America/Los_Angeles')
    dt = pacific_timezone.localize(dt)

    return dt.date()  # 返回日期部分，去除时间

def calculate_date(current_date, date_str):
    today = parse_datetime(current_date)
    
    # 处理 "today" 和 "yesterday"
    if date_str == "today":
        return today
    elif date_str == "yesterday":
        return today - datetime.timedelta(days=1)

    # 处理 "last Monday" 到 "last Sunday"
    weekdays = {
        "last sunday": 7,
        "last monday": 6,
        "last tuesday": 5,
        "last wednesday": 4,
        "last thursday": 3,
        "last friday": 2,
        "last saturday": 1,
    }

    this_sunday = today - datetime.timedelta(days=today.weekday() + 1)

    return this_sunday - datetime.timedelta(days=weekdays[date_str])

def find_date_from_text(current_date:str, text:str):
    """
    Returns the date described in the text relative to the current date.
    args:
        current_date: str, current date in the format of "MM/DD/YYYY, HH:MM:SS PT"
        text: str, text containing date description
    output:
        date: str, format: 'YYYY-MM-DD'
        date_str: str, description of the date
    """
    # 正则表达式匹配各种日期描述
    pattern1 = r"(last|past|previous|recent)"
    pattern2 = r"(mon|tues|wednes|thurs|fri|satur|sun)"
    pattern3 = r"(today|yesterday)"
    match1 = re.search(pattern1, text)
    match2 = re.search(pattern2, text)
    match3 = re.search(pattern3, text)

    if match1 and match2 or match3:
        if match1:
            date_str = "last " + match2.group(0) + "day"
        else:
            date_str = match3.group(0)
    else:
        return None, None

    # 返回相应的日期
    return calculate_date(current_date, date_str).strftime('%Y-%m-%d'), date_str

def find_date_from_text_all(current_date:str, text:str):
    pattern1 = r"(last|past|previous|recent)"
    pattern2 = r"(mon|tues|wednes|thurs|fri|satur|sun)"
    pattern3 = r"(today|yesterday)"
    match1 = re.search(pattern1, text)
    match2 = re.search(pattern2, text)
    match3 = re.findall(pattern3, text)

    if match1 and match2:
        date_str = "last " + match2.group(0) + "day"
        date = calculate_date(current_date, date_str).strftime('%Y-%m-%d')
        dates_str = [date_str]
        dates = [date]
    elif match3:
        dates_str = match3
        dates = [calculate_date(current_date, date_str).strftime('%Y-%m-%d') for date_str in dates_str]
    else:
        return [], []
    
    return dates, dates_str

def get_last_week_dates(current_date:str):
    """
    Returns the dates of last week.
    args:
        current_date: str, current date in the format of "MM/DD/YYYY, HH:MM:SS PT"
    output:
        date: list[str], format: 'YYYY-MM-DD'
    """
    today = parse_datetime(current_date)
    current_weekday = today.weekday()
    last_sunday = today - datetime.timedelta(days=current_weekday + 1)
    
    dates = [last_sunday - datetime.timedelta(days=i) for i in range(1,8)]
    return [date.strftime('%Y-%m-%d') for date in dates]

def get_last_month_dates(current_date:str) -> str:
    """
    Returns the dates of last month.
    args:
        current_date: str, current date in the format of "MM/DD/YYYY, HH:MM:SS PT"
    output:
        date: list[str], format: 'YYYY-MM-DD'
    """
    # 获取当前日期
    today = parse_datetime(current_date)

    # 计算上个月的第一天
    first_day_of_current_month = today.replace(day=1)
    last_day_of_last_month = first_day_of_current_month - datetime.timedelta(days=1)
    first_day_of_last_month = last_day_of_last_month.replace(day=1)

    # 计算上个月的日期
    dates = [first_day_of_last_month + datetime.timedelta(days=i) for i in range((last_day_of_last_month - first_day_of_last_month).days + 1)]
    return [date.strftime('%Y-%m-%d') for date in dates]

def get_this_week_dates(current_date:str) -> str:
    """
    Returns the dates of this week.
    args:
        current_date: str, current date in the format of "MM/DD/YYYY, HH:MM:SS PT"
    output:
        date: list[str], format: 'YYYY-MM-DD'
    """
    today = parse_datetime(current_date)
    current_weekday = today.weekday()
    last_sunday = today - datetime.timedelta(days=current_weekday + 1)

    # 计算本周的日期
    dates = [last_sunday + datetime.timedelta(days=i) for i in range(7)]
    return [date.strftime('%Y-%m-%d') for date in dates]

def get_this_month_dates(current_date:str) -> str:
    """
    Returns the dates of this month.
    args:
        current_date: str, current date in the format of "MM/DD/YYYY, HH:MM:SS PT"
    output:
        date: list[str], format: 'YYYY-MM-DD'
    """
    # 获取当前日期
    today = parse_datetime(current_date)

    # 计算本月的第一天
    first_day_of_current_month = today.replace(day=1)

    # 计算本月的日期，不算今天
    dates = [first_day_of_current_month + datetime.timedelta(days=i) for i in range(today.day)]
    return [date.strftime('%Y-%m-%d') for date in dates]

def extract_date(text:str) -> str:
    """
    Returns the date described in the text.
    args:
        text: str, text containing date description
    output:
        year: str, format: 'YYYY'
        month: str, format: 'MM'
        day: str, format: 'DD'
    """
    # 正则表达式匹配日期
    pattern = r"(\d{4})-(\d{2})-(\d{2})"
    match = re.search(pattern, text)

    if not match:
        pattern = r"(\d{4})-(\d{2})"
        match = re.search(pattern, text)
        if not match:
            pattern = r"(\d{4})"
            match = re.search(pattern, text)
            if not match:
                return None, None, None
            else:
                return match.group(1), None, None
        else:
            return match.group(1), match.group(2), None
    else:
        return match.group(1), match.group(2), match.group(3)
    
def extract_date_(text:str) -> str:
    """
    Returns the date described in the text.
    args:
        text: str, text containing date description
    output:
        date: str, format: 'YYYY-MM-DD'
    """
    text = text.replace(",", "")
    # 找到text中形如 jan 1 2021 或 january 1 2021 的日期字符串，并转换为 2021-01-01 的格式
    pattern = r"([A-Za-z]+) (\d{1,2}) (\d{4})"
    match = re.search(pattern, text)
    if match:
        month = match.group(1).lower()
        day = match.group(2)
        if len(day) == 1:
            day = "0" + day
        year = match.group(3)
        month_dict = {
            "jan": "01",
            "feb": "02",
            "mar": "03",
            "apr": "04",
            "may": "05",
            "jun": "06",
            "jul": "07",
            "aug": "08",
            "sep": "09",
            "oct": "10",
            "nov": "11",
            "dec": "12",
            "january": "01",
            "february": "02",
            "march": "03",
            "april": "04",
            # "may": "05",
            "june": "06",
            "july": "07",
            "august": "08",
            "september": "09",
            "october": "10",
            "november": "11",
            "december": "12",
        }
        month = month_dict[month]
        return f"{year}-{month}-{day}"

    return None
    
    