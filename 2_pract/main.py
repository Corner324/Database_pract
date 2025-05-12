from datetime import date

from spimex_parser import process_bulletins

if __name__ == "__main__":
    start_date = date(2025, 4, 22)
    end_date = date(2025, 5, 11)
    process_bulletins(start_date, end_date)
