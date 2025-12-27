import os
import pandas as pd

class Olist:
    def get_data(self):
        """
        Bu fonksiyon bir Python sözlüğü (dict) döndürür.
        Anahtarlar: 'sellers', 'orders', 'order_items' vb.
        Değerler: pandas DataFrame olarak yüklenmiş CSV dosyaları
        """
        root_dir = os.path.dirname(os.path.dirname(__file__))
        csv_path = os.path.join(root_dir, 'data', 'csv')

        file_names = [f for f in os.listdir(csv_path) if f.endswith('.csv')]

        key_names = [
            name.replace(".csv", "")
            .replace("_dataset", "")
            .replace("olist_", "")
            for name in file_names
        ]

        data = {}
        for key, file in zip(key_names, file_names):
            full_path = os.path.join(csv_path, file)
            data[key] = pd.read_csv(full_path)

        return data
    