import pandas as pd
import numpy as np
from olist.data import Olist

class Order:
    def get_wait_time(self, is_delivered=True):
        # 1. Veriyi Olist sınıfından çek
        orders = Olist().get_data()['orders'].copy()

        # 2. is_delivered True ise sadece teslim edilenleri al
        if is_delivered:
            orders = orders[orders['order_status'] == 'delivered']

        # 3. Tarih formatına çevir
        date_cols = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date']
        for col in date_cols:
            orders[col] = pd.to_datetime(orders[col])

        # 4. wait_time hesapla
        one_day = np.timedelta64(24, 'h')
        orders['wait_time'] = (orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']) / one_day

        # 5. expected_wait_time hesapla
        orders['expected_wait_time'] = (orders['order_estimated_delivery_date'] - orders['order_purchase_timestamp']) / one_day

        # 6. delay_vs_expected hesapla
        orders['delay_vs_expected'] = (orders['order_delivered_customer_date'] - orders['order_estimated_delivery_date']) / one_day
        orders.loc[orders['delay_vs_expected'] < 0, 'delay_vs_expected'] = 0

        # 7. Sonuçları döndür
        return orders[['order_id', 'wait_time', 'expected_wait_time', 'delay_vs_expected', 'order_status']]

    def get_review_score(self):
        # 1. Veriyi çek
        reviews = Olist().get_data()['order_reviews'].copy()
        
        # 2. 5 yıldız ve 1 yıldız durumlarını kodla (1/0)
        reviews['dim_is_five_star'] = (reviews['review_score'] == 5).astype(int)
        reviews['dim_is_one_star'] = (reviews['review_score'] == 1).astype(int)
        
        # 3. İstenen sütunları döndür
        return reviews[['order_id', 'dim_is_five_star', 'dim_is_one_star', 'review_score']]

    def get_number_items(self):
        items = Olist().get_data()['order_items'].copy()
        items = items.groupby('order_id').agg({'product_id': 'count'})
        items.rename(columns={'product_id': 'number_of_items'}, inplace=True)
        items.reset_index(inplace=True)  # <-- Bunu ekledik
        return items

    def get_number_sellers(self):
        pass

    def get_price_and_freight(self):
        pass

    def get_training_data(self, is_delivered=True, with_distance_seller_customer=False):
        pass