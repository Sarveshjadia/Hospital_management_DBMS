from main import app, db

with app.app_context():
    print("\n======================================")
    print("  CONNECTED DATABASE →", db.engine.url.database)
    print("======================================\n")

    # Patients table count check
    try:
        from main import Patients
        count = db.session.query(Patients).count()
        print(f"PATIENTS RECORD FOUND → {count}")
    except:
        print("Patients Table Not Found ❌")
