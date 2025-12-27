import pandas as pd
import numpy as np
from olist.data import Olist
from olist.utils import haversine_distance

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

    def get_distance_seller_customer(self):
        # 1. Verileri çek
        data = Olist().get_data()
        orders = data['orders']
        items = data['order_items']
        sellers = data['sellers']
        customers = data['customers']
        geo = data['geolocation']

        # 2. Sadece teslim edilenler
        orders = orders[orders['order_status'] == 'delivered']

        # 3. Geo verisini tekilleştir
        geo = geo.groupby('geolocation_zip_code_prefix').first().reset_index()

        # 4. Merge işlemleri
        merged = orders.merge(items, on='order_id') \
                       .merge(sellers, on='seller_id') \
                       .merge(customers, on='customer_id')

        # 5. Müşteri koordinatları
        merged = merged.merge(geo, left_on='customer_zip_code_prefix', right_on='geolocation_zip_code_prefix', how='left')
        merged.rename(columns={'geolocation_lat': 'c_lat', 'geolocation_lng': 'c_lng'}, inplace=True)

        # 6. Satıcı koordinatları
        merged = merged.merge(geo, left_on='seller_zip_code_prefix', right_on='geolocation_zip_code_prefix', how='left')
        merged.rename(columns={'geolocation_lat': 's_lat', 'geolocation_lng': 's_lng'}, inplace=True)

        # 7. Eksik verileri at
        merged = merged.dropna(subset=['c_lat', 'c_lng', 's_lat', 's_lng'])

        # 8. Mesafeyi hesapla
        merged['distance_seller_customer'] = merged.apply(
            lambda row: haversine_distance(row['c_lng'], row['c_lat'], row['s_lng'], row['s_lat']), 
            axis=1
        )

        # 9. Ortalama al ve döndür
        unique_dist = merged.groupby('order_id').agg({'distance_seller_customer': 'mean'}).reset_index()
        return unique_dist

    def get_training_data(self, is_delivered=True, with_distance_seller_customer=False):
        training_data = self.get_wait_time(is_delivered=is_delivered)
        
        training_data = training_data.merge(self.get_review_score(), on='order_id') \
                                     .merge(self.get_number_items(), on='order_id') \
                                     .merge(self.get_number_sellers(), on='order_id') \
                                     .merge(self.get_price_and_freight(), on='order_id')
        
        if with_distance_seller_customer:
            training_data = training_data.merge(self.get_distance_seller_customer(), on='order_id')
        
        training_data = training_data.dropna()
        return training_data