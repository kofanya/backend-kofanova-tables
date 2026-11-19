from database import SessionLocal
from models import Table

def seed_data():
    db = SessionLocal()
    if db.query(Table).count() == 0:
        tables = [
            Table(number="1A", capacity=2, zone="Окно"),
            Table(number="2B", capacity=4, zone="Терраса"),
            Table(number="3C", capacity=6, zone="Зал")
        ]
        db.add_all(tables)
        db.commit()
        print("База  заполнена тестовыми данными")
    else:
        print("В базе уже есть данные")
    db.close()

if __name__ == "__main__":
    seed_data()