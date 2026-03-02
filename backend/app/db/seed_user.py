from app.db.database import SessionLocal, engine
from app.db.models import User, Base
from app.auth.security import hash_password


def seed():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    
    existing = db.query(User).filter(User.username == 'admin').first()
    if existing:
        print("Admin already exists. ")
        return
    
    hashed = hash_password('pass123')
    
    admin = User(
        username = 'admin',
        role = 'admin',
        password_hash = hashed
        )
        
    db.add(admin)
    db.commit()
    db.close()
    print('Admin created, username = admin, password = pass123')
if __name__ == '__main__':
    seed()    