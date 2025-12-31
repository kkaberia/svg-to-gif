from app import app, db, User  # Import your Flask app, db, and User model

# Set up the application context
with app.app_context():
    # Fetch the user with username 'kkaberia'
    user = User.query.filter_by(username='kkaberia').first()

    if user:
        # Update the opening_balance to 0.0
        user.opening_balance = 0.0
        db.session.commit()  # Commit the changes to the database
        print(f"Updated opening_balance for user 'kkaberia' to 0.0.")
    else:
        print("User 'kkaberia' not found in the database.")