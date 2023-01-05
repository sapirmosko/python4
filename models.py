from DBManager import db
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base


class videos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    video_path = db.Column(db.String(2000))
    frames_num = db.Column(db.Integer)


class metadata(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(1000))
    fov = db.Column(db.Float)
    azimuth = db.Column(db.Float)
    elevation = db.Column(db.Float)


class frames(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    frame_path = db.Column(db.String(2000))
    index = db.Column(db.Integer)
    metadata_id = db.Column(db.Integer, ForeignKey(
        'metadata.id'), nullable=False)
    video_id = db.Column(db.Integer, ForeignKey('videos.id'), nullable=False)

    metadataR = relationship('metadata', foreign_keys='frames.metadata_id')
    videosR = relationship('videos', foreign_keys='frames.video_id')
