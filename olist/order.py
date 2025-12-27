import pandas as pd
import numpy as np
from olist.data import Olist

class Order:
    def get_wait_time(self, is_delivered=True):
        # 1. Veriyi çek
        orders = Olist().get_data()['orders'].copy()
        
        # 2. Teslim edilenleri filtrele
        if is_delivered:
            orders = orders[orders['order_status'] == 'delivered']
        
        # 3. Tarih formatına çevir
        date_cols = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']
        for col in date_cols:
            orders[col] = pd.to_datetime(orders[col])

        # 4. Hesaplamaları yap
        one_day = np.timedelta64(24, 'h')
        orders['wait_time'] = (orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']) / one_day
        orders['expected_wait_time'] = (orders['order_estimated_delivery_date'] - orders['order_purchase_timestamp']) / one_day
        orders['delay_vs_expected'] = (orders['order_delivered_customer_date'] - orders['order_estimated_delivery_date']) / one_day
        orders.loc[orders['delay_vs_expected'] < 0, 'delay_vs_expected'] = 0
        
        return orders[['order_id', 'wait_time', 'expected_wait_time', 'delay_vs_expected', 'order_status']]

    def get_review_score(self):
        pass

    def get_number_items(self):
        pass

    def get_number_sellers(self):
        pass

    def get_price_and_freight(self):
        pass

    def get_training_data(self, is_delivered=True, with_distance_seller_customer=False):
        pass
    