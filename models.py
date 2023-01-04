from app import db


class videos(db.Model):
    id = db.Column('video_id', db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    video_path = db.Column(db.String(100))
    frames_num = db.Column(db.Integer)


class metadata(db.Model):
    id = db.Column('metadata_id', db.Integer, primary_key=True)
    tag = db.Column(db.String(100))
    fov = db.Column(db.Float)
    azimuth = db.Column(db.Float)
    elevation = db.Column(db.Float)


class frames(db.Model):
    id = db.Column('frames_id', db.Integer, primary_key=True)
    frame_path = db.Column(db.String(100))
    index = db.Column(db.Integer)
    metadata_id = db.Column(db.Integer)
    video_id = db.Column(db.Integer)

