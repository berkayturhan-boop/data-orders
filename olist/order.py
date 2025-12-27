import pandas as pd
import numpy as np
from olist.data import Olist

class Order:
    def get_wait_time(self, is_delivered=True):
        orders = Olist().get_data()['orders'].copy()
        if is_delivered:
            orders = orders[orders['order_status'] == 'delivered']
        
        date_cols = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']
        for col in date_cols:
            orders[col] = pd.to_datetime(orders[col])

        one_day = np.timedelta64(24, 'h')
        orders['wait_time'] = (orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']) / one_day
        orders['expected_wait_time'] = (orders['order_estimated_delivery_date'] - orders['order_purchase_timestamp']) / one_day
        orders['delay_vs_expected'] = (orders['order_delivered_customer_date'] - orders['order_estimated_delivery_date']) / one_day
        orders.loc[orders['delay_vs_expected'] < 0, 'delay_vs_expected'] = 0
        
        return orders[['order_id', 'wait_time', 'expected_wait_time', 'delay_vs_expected', 'order_status']]

    def get_review_score(self):
        reviews = Olist().get_data()['order_reviews'].copy()
        reviews['dim_is_five_star'] = (reviews['review_score'] == 5).astype(int)
        reviews['dim_is_one_star'] = (reviews['review_score'] == 1).astype(int)
        return reviews[['order_id', 'dim_is_five_star', 'dim_is_one_star', 'review_score']]

    def get_number_items(self):
        items = Olist().get_data()['order_items'].copy()
        items = items.groupby('order_id').agg({'product_id': 'count'})
        items.rename(columns={'product_id': 'number_of_items'}, inplace=True)
        items.reset_index(inplace=True)
        return items

    def get_number_sellers(self):
        sellers = Olist().get_data()['order_items'].copy()
        sellers = sellers.groupby('order_id').agg({'seller_id': 'nunique'})
        sellers.rename(columns={'seller_id': 'number_of_sellers'}, inplace=True)
        sellers.reset_index(inplace=True)
        return sellers

    def get_price_and_freight(self):
        price = Olist().get_data()['order_items'].copy()
        price = price.groupby('order_id')[['price', 'freight_value']].sum()
        price.reset_index(inplace=True)
        return price

    def get_training_data(self, is_delivered=True, with_distance_seller_customer=False):
        # 1. Ana veriyi (wait_time) al
        training_data = self.get_wait_time(is_delivered=is_delivered)
        
        # 2. Diğer özellikleri merge et
        training_data = training_data.merge(self.get_review_score(), on='order_id') \
                                     .merge(self.get_number_items(), on='order_id') \
                                     .merge(self.get_number_sellers(), on='order_id') \
                                     .merge(self.get_price_and_freight(), on='order_id')
        
        # 3. Eksik verileri temizle (dropna)
        training_data = training_data.dropna()
        
        return training_data