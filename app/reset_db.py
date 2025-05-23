from app.database import engine, Base

# DANGER: This will drop and recreate all tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

print("Database has been reset.")