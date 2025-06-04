from db.repositories import auctioneer
from db.traider import trader
from gui_utils.utils import GUI
from history.upload import init_history
from items.upload import init_items
from professions.upload import init_professions

init_items()
init_history()
init_professions()

recipes = trader.print_craft(min_profit=10, max_profit=30)
items = trader.print_buy(min_profit=10, max_profit=30)

p = auctioneer.get_item_price('Пыль провидения')

gui = GUI(recipes, 'Перегруженный конденсатор')
gui.buy_recipe(3)

gui.gui_buy()



