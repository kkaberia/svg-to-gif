# Add year field to Payment model
class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_type = db.Column(db.String(50))
    origin_bank = db.Column(db.String(50), nullable=True)
    months = db.Column(db.String(100), nullable=True)
    year = db.Column(db.Integer, default=lambda: datetime.now().year)  # ADD THIS LINE