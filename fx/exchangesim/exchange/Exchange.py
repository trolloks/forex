from queue import Queue
from threading import Thread
import asyncio
import datetime
import websockets
import time

from fx.exchangesim.exchange.OrderDao import OrderDao
from fx.exchangesim.exchange.OrderMatcher import OrderMatcher
from fx.exchangesim.trader.TraderSimulator import TraderSimulator

q = Queue()  # TODO set size?
output = Queue() #TODO separate buy and sell queue?


def producer():
    ts = TraderSimulator()
    ts.start(q)

#TODO write tests
def consumer():
    order_dao = OrderDao()
    order_matcher = OrderMatcher(order_dao)
    while True:
        order = q.get()
        if order.order_size <= 0:
            continue
        if not order_dao.contains(order):  # Already in the order book
            add_to_order_book(order, order_dao)
        matched_order = order_matcher.match(order)  # TODO match against queue and database
        if matched_order is not None:
            handle_matched_order(matched_order, order, order_dao)
        else:
            handle_unmatched_order(order, order_dao)


def handle_unmatched_order(order, order_dao):
    # print("!Failed to match order #%s" % order.order_id)
    q.put(order)
    order_dao.persist(order)  # persist to the order book with other yet-unmatched orders
    time.sleep(1)
    # TODO only keep highest precendence orders in queue, for efficiency?


def add_to_order_book(order, order_dao):
    order_dao.persist(order)
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    print(now + " > Received order #%s" % order.order_id)
    output.put(str(order))  # TODO output time too?


def handle_matched_order(matched_order, order, order_dao):
    original_order_size = order.order_size
    original_matched_order_size = matched_order.order_size
    order.order_size = original_order_size - original_matched_order_size
    matched_order.order_size = original_matched_order_size - original_order_size
    if order.order_size <= 0:
        order.order_size = 0
        order_dao.remove(order)
        output.put("Filled %s" % order.order_id)
    else:
        q.put(order)  # TODO do we lose FIFO ordering?
        output.put("Partial: %s,Original: %d,Current: %d"
                   % (order.order_id, original_order_size, order.order_size))
    if matched_order.order_size <= 0:
        matched_order.order_size = 0
        order_dao.remove(matched_order)
        output.put("Filled %s" % matched_order.order_id)
    else:
        output.put("Partial: %s,Original: %d,Current: %d"
                   % (matched_order.order_id, original_matched_order_size, matched_order.order_size))
        # q.put(matched_order)
    output.put("Matched order #%s (%d before, %d after) with #%s (%d before, %d after)"
               % (order.order_id, original_order_size, order.order_size, matched_order.order_id,
                  original_matched_order_size, matched_order.order_size))
    # TODO update UI (bid, ask, last)


@asyncio.coroutine
def main(websocket, path):
    prod = Thread(target=producer)
    prod.start()
    cons = Thread(target=consumer)
    cons.start()
    while True:
        if not websocket.open:
            break
        message = output.get()
        yield from websocket.send(message)


start_server = websockets.serve(main, '127.0.0.1', 5678)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()