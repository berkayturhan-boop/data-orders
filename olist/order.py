import pandas as pd
import numpy as np
from olist.data import Olist

class Order:
    def get_wait_time(self, is_delivered=True):
        """
        02-01 > Order.get_wait_time
        DataFrame döndürür: [order_id, wait_time, expected_wait_time, delay_vs_expected, order_status]
        """
        # 1. Veriyi Olist'ten çek
        orders = Olist().get_data()['orders'].copy()

        # 2. Sadece teslim edilenleri filtrele
        if is_delivered:
            orders = orders[orders['order_status'] == 'delivered']

        # 3. Tarih dönüşümleri (String -> Datetime)
        date_cols = ['order_purchase_timestamp', 
                     'order_approved_at', 
                     'order_delivered_carrier_date', 
                     'order_delivered_customer_date', 
                     'order_estimated_delivery_date']
        
        for col in date_cols:
            orders[col] = pd.to_datetime(orders[col])

        # 4. Hesaplamalar
        one_day = np.timedelta64(24, 'h')

        # wait_time
        orders['wait_time'] = (orders['order_delivered_customer_date'] - orders['order_purchase_timestamp']) / one_day

        # expected_wait_time
        orders['expected_wait_time'] = (orders['order_estimated_delivery_date'] - orders['order_purchase_timestamp']) / one_day

        # delay_vs_expected
        orders['delay_vs_expected'] = (orders['order_delivered_customer_date'] - orders['order_estimated_delivery_date']) / one_day

        # Erken gelenleri (negatifleri) 0 yap
        orders.loc[orders['delay_vs_expected'] < 0, 'delay_vs_expected'] = 0

        # 5. Sütunları seç ve döndür
        return orders[['order_id', 'wait_time', 'expected_wait_time', 'delay_vs_expected', 'order_status']]

    def get_review_score(self):
        """
        DataFrame döndürür: [order_id, review_score, dim_is_five_star, dim_is_one_star]
        """
        reviews = Olist().get_data()['order_reviews']
        
        # Mükerrer yorumları önlemek için basit bir gruplama yapabiliriz veya direkt alabiliriz.
        # Şimdilik review_score ve order_id'yi alıyoruz.
        
        # Ekstra özellikler: 5 yıldız mı? 1 yıldız mı?
        reviews['dim_is_five_star'] = reviews['review_score'].apply(lambda x: 1 if x == 5 else 0)
        reviews['dim_is_one_star'] = reviews['review_score'].apply(lambda x: 1 if x == 1 else 0)
        
        return reviews[['order_id', 'review_score', 'dim_is_five_star', 'dim_is_one_star']]

    def get_number_products(self):
        """
        DataFrame döndürür: [order_id, number_of_products]
        """
        data = Olist().get_data()['order_items']
        # order_id'ye göre say
        products = data.groupby('order_id').count()
        # Herhangi bir sütunu (mesela order_item_id) saydırmak yeterli
        products = products[['order_item_id']].rename(columns={'order_item_id': 'number_of_products'})
        return products

    def get_number_sellers(self):
        """
        DataFrame döndürür: [order_id, number_of_sellers]
        """
        data = Olist().get_data()['order_items']
        # order_id'ye göre grupla ve seller_id'nin benzersiz sayısını (nunique) al
        sellers = data.groupby('order_id')['seller_id'].nunique().reset_index()
        sellers.columns = ['order_id', 'number_of_sellers']
        return sellers

    def get_price_and_freight(self):
        """
        DataFrame döndürür: [order_id, price, freight_value]
        """
        data = Olist().get_data()['order_items']
        # order_id'ye göre grupla ve fiyatları topla
        price_freight = data.groupby('order_id')[['price', 'freight_value']].sum().reset_index()
        return price_freight
    