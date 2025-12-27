import numpy as np

def haversine_distance(lon1, lat1, lon2, lat2):
    """
    İki koordinat (lon1, lat1, lon2, lat2) arasındaki mesafeyi hesaplar.
    Sonuç kilometre (km) cinsindendir.
    """
    # Dereceleri radyana çevir
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    # Haversine formülü
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    # Dünya'nın yarıçapı (km)
    km = 6371 * c
    return km
