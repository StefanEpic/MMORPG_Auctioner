from pprint import pprint

from db.repositories import auctioneer
from db.traider import trader
from history.upload import init_history, add_history
from professions.upload import init_professions

# init_history()
# add_history('2025_05_29.txt')
# init_professions()

trader.print_craft(min_profit=10, max_profit=30)
trader.print_buy(min_profit=10, max_profit=30)
