from app.extensions import db

class InGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    score = db.Column(db.Integer)
    round = db.Column(db.Integer)

    def __init__(self, name, score=0, round=0):
        self.name = name
        self.score = score
        self.round = round
