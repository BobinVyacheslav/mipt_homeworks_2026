#!/usr/bin/env python

import sys
from typing import Any, Final

UNKNOWN_COMMAND_MSG: Final = "Unknown command!"
NONPOSITIVE_VALUE_MSG: Final = "Value must be grater than zero!"
INCORRECT_DATE_MSG: Final = "Invalid date!"
NOT_EXISTS_CATEGORY: Final = "Category not exists!"
OP_SUCCESS_MSG: Final = "Added"

FEBRUARY: Final = 2
APRIL: Final = 4
JUNE: Final = 6
SEPTEMBER: Final = 9
NOVEMBER: Final = 11

THIRTY_DAYS: Final = 30
THIRTY_ONE_DAYS: Final = 31
TWENTY_EIGHT_DAYS: Final = 28
TWENTY_NINE_DAYS: Final = 29

LEAP_YEAR_DIVISOR_FOUR: Final = 4
LEAP_YEAR_DIVISOR_ONE_HUNDRED: Final = 100
LEAP_YEAR_DIVISOR_FOUR_HUNDRED: Final = 400

DATE_LEN: Final = 10

MAX_MONTH_NUMBER: Final = 12
PARTS_IN_CATEGORY: Final = 2

FIRST_DASH_POSITION: Final = 2
SECOND_DASH_POSITION: Final = 5

INCOME_COMMAND_LENGTH: Final = 3
COST_CATEGORY_COMMAND_LENGTH: Final = 2
COST_COMMAND_LENGTH: Final = 4
STATS_COMMAND_LENGTH: Final = 2

ZERO_FLOAT: Final = float(0)

KEY_TYPE: Final = "type"
KEY_AMOUNT: Final = "amount"
KEY_DATE: Final = "date"
KEY_CATEGORY: Final = "category"

TYPE_INCOME: Final = "income"
TYPE_COST: Final = "cost"

financial_transactions_storage: list[dict[str, Any]] = []

EXPENSE_CATEGORIES: dict[str, tuple[str, ...]] = {
    "Food": ("Supermarket", "Restaurants", "FastFood", "Coffee", "Delivery"),
    "Transport": ("Taxi", "Public transport", "Gas", "Car service"),
    "Housing": ("Rent", "Utilities", "Repairs", "Furniture"),
    "Health": ("Pharmacy", "Doctors", "Dentist", "Lab tests"),
    "Entertainment": ("Movies", "Concerts", "Games", "Subscriptions"),
    "Clothing": ("Outerwear", "Casual", "Shoes", "Accessories"),
    "Education": ("Courses", "Books", "Tutors"),
    "Communications": ("Mobile", "Internet", "Subscriptions"),
    "Other": ("SomeCategory", "SomeOtherCategory"),
}


def is_leap_year(year: int) -> bool:
    """
        Для заданного года определяет: високосный (True) или невисокосный (False).

        :param int year: Проверяемый год
        :return: Значение високосности.
        :rtype: bool
        """
    if year % LEAP_YEAR_DIVISOR_FOUR_HUNDRED == 0:
        return True
    if year % LEAP_YEAR_DIVISOR_ONE_HUNDRED == 0:
        return False
    return year % LEAP_YEAR_DIVISOR_FOUR == 0


def get_days_in_month(month: int, year: int) -> int:
    if month in {APRIL, JUNE, SEPTEMBER, NOVEMBER}:
        return THIRTY_DAYS
    if month == FEBRUARY:
        return TWENTY_NINE_DAYS if is_leap_year(year) else TWENTY_EIGHT_DAYS
    return THIRTY_ONE_DAYS


def has_valid_date_format(date_string: str) -> bool:
    if len(date_string) != DATE_LEN:
        return False
    if date_string[FIRST_DASH_POSITION] != "-":
        return False
    return date_string[SECOND_DASH_POSITION] == "-"


def extract_date(maybe_dt: str) -> tuple[int, int, int] | None:
    """
        Парсит дату формата DD-MM-YYYY из строки.

        :param str maybe_dt: Проверяемая строка
        :return: tuple формата (день, месяц, год) или None, если дата неправильная.
        :rtype: tuple[int, int, int] | None
        """
    if not has_valid_date_format(maybe_dt):
        return None

    raw_parts = [maybe_dt[:2],
                 maybe_dt[3:5],
                 maybe_dt[6:]]
    if not all(part.isdigit() for part in raw_parts):
        return None

    day, month, year = map(int, raw_parts)

    if month < 1 or month > MAX_MONTH_NUMBER or year < 1:
        return None

    if day < 1 or day > get_days_in_month(month, year):
        return None

    return day, month, year


def is_valid_category(category_string: str) -> bool:
    if "::" not in category_string:
        return False
    category_parts = category_string.split("::")
    if len(category_parts) != PARTS_IN_CATEGORY:
        return False
    common, target = category_parts
    categories = EXPENSE_CATEGORIES
    return common in categories and target in categories[common]


def income_handler(amount: float, income_date: str) -> str:
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    parsed_date = extract_date(income_date)
    if parsed_date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append(
        {
            KEY_TYPE: TYPE_INCOME,
            KEY_AMOUNT: amount,
            KEY_DATE: parsed_date,
        }
    )
    return OP_SUCCESS_MSG


def cost_categories_handler() -> str:
    category_lines: list[str] = []
    for common, targets in EXPENSE_CATEGORIES.items():
        category_lines.extend(f"{common}::{target}" for target in targets)
    return "\n".join(category_lines)


def cost_handler(category_name: str, amount: float, income_date: str) -> str:
    if not is_valid_category(category_name):
        financial_transactions_storage.append({})
        return NOT_EXISTS_CATEGORY
    if amount <= 0:
        financial_transactions_storage.append({})
        return NONPOSITIVE_VALUE_MSG
    parsed_date = extract_date(income_date)
    if parsed_date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    financial_transactions_storage.append(
        {
            KEY_TYPE: TYPE_COST,
            KEY_CATEGORY: category_name,
            KEY_AMOUNT: amount,
            KEY_DATE: parsed_date,
        }
    )
    return OP_SUCCESS_MSG


def get_capital_at(day: int, month: int, year: int) -> float:
    total_capital = ZERO_FLOAT
    for transaction in financial_transactions_storage:
        if not transaction:
            continue
        t_day, t_month, t_year = transaction[KEY_DATE]
        if (t_year, t_month, t_day) <= (year, month, day):
            if transaction[KEY_TYPE] == TYPE_INCOME:
                total_capital += transaction[KEY_AMOUNT]
            else:
                total_capital -= transaction[KEY_AMOUNT]
    return total_capital


def _update_totals(transaction: dict[str, Any],
                   totals: list[int | float],
                   category_totals: dict[str, float]) -> None:
    amount = transaction[KEY_AMOUNT]
    if transaction[KEY_TYPE] == TYPE_INCOME:
        totals[0] += amount
    else:
        totals[1] += amount
        target = transaction[KEY_CATEGORY].split("::")[1]
        category_totals[target] = category_totals.get(target, ZERO_FLOAT) + amount


def get_monthly_stats(month: int, year: int) -> tuple[float, float, dict[str, float]]:
    totals = [ZERO_FLOAT, ZERO_FLOAT]
    category_totals: dict[str, float] = {}

    for transaction in financial_transactions_storage:
        if not transaction:
            continue
        if (transaction[KEY_DATE][1] == month
                and transaction[KEY_DATE][2] == year):
            _update_totals(transaction, totals, category_totals)

    return totals[0], totals[1], category_totals


def format_stats(
    date_string: str,
    capital: float,
    income: float,
    expenses: float,
    category_totals: dict[str, float],
) -> str:
    diff = income - expenses
    res_type = "profit" if diff >= 0 else "loss"

    lines = [
        f"Your statistics as of {date_string}:",
        f"Total capital: {capital:.2f} rubles",
        f"This month, the {res_type} amounted to {abs(diff):.2f} rubles.",
        f"Income: {income:.2f} rubles",
        f"Expenses: {expenses:.2f} rubles",
        "",
        "Details (category: amount):",
    ]

    for index, name in enumerate(sorted(category_totals.keys()), 1):
        lines.append(f"{index}. {name}: {category_totals[name]:.2f}")

    return "\n".join(lines)


def stats_handler(report_date: str) -> str:
    parsed_date = extract_date(report_date)
    if parsed_date is None:
        financial_transactions_storage.append({})
        return INCORRECT_DATE_MSG

    capital = get_capital_at(*parsed_date)
    income, expenses, category_totals = get_monthly_stats(parsed_date[1], parsed_date[2])

    return format_stats(report_date, capital, income, expenses, category_totals)


def parse_amount(amount_string: str) -> float | None:
    normalized_amount = amount_string.replace(",", ".")
    decimal_points_count = 0

    for character in normalized_amount:
        if character == ".":
            decimal_points_count += 1
        elif not character.isdigit():
            return None

    if decimal_points_count > 1:
        return None

    return float(normalized_amount)


def _execute_income(arguments: list[str]) -> str:
    if len(arguments) != INCOME_COMMAND_LENGTH:
        return UNKNOWN_COMMAND_MSG
    amount = parse_amount(arguments[1])
    return income_handler(-1.0 if amount is None else amount, arguments[2])


def _execute_cost(arguments: list[str]) -> str:
    if len(arguments) == COST_CATEGORY_COMMAND_LENGTH and arguments[1] == "categories":
        return cost_categories_handler()
    if len(arguments) == COST_COMMAND_LENGTH:
        amount = parse_amount(arguments[2])
        return cost_handler(arguments[1],
                            -1.0 if amount is None else amount,
                            arguments[3])
    return UNKNOWN_COMMAND_MSG


def execute_command(arguments: list[str]) -> str:
    command_name = arguments[0]
    match command_name:
        case "income":
            return _execute_income(arguments)
        case "cost":
            return _execute_cost(arguments)
        case "stats":
            if len(arguments) == STATS_COMMAND_LENGTH:
                return stats_handler(arguments[1])
    return UNKNOWN_COMMAND_MSG


def main() -> None:
    for line in sys.stdin:
        command_parts = line.split()
        if command_parts:
            print(execute_command(command_parts))


if __name__ == "__main__":
    main()
