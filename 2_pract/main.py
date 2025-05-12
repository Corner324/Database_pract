import asyncio
from datetime import date

from spimex_parser import process_bulletins

if __name__ == "__main__":
    asyncio.run(process_bulletins(date(2023, 4, 22), date(2025, 5, 11)))
