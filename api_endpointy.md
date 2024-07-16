# Endpointy

Veškerá data využitá na webové stránce jsou dostupná skrze endpointy, vypsány jsou níže:

- `/api/values`: metadata parametrů
- `/api/stations`: metadata stanic
- `/api/station/geo/`: metadata se souřadnicemi, GeoJSON
- `/api/station/<id_stanice>`: základní metadata zvolené stanice
- `/api/station/<id_stanice>/values`: měřené parametry zvolené stanice
- `/api/station/<id_stanice>/year`: roky měření zvolené stanice
- `/api/station/<id_stanice>/data`: všechna data zvolené stanice
- `/api/station/<id_stanice>/<parametr>/dataseries`: data zvolené stanice a parametru
- `/api/station/<id_stanice>/<parametr>/percentiles`: měsíční percentily zvolené stanice a parametru
- `/api/station/<id_stanice>/<parametr>/<rok>/yearly-data`: data zvoleného parametru a roku