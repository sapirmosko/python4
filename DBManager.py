import os
import json
import models
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class DBManager:
    def __init__(self, app):
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
        username = os.getenv('USER_NAME')
        password = os.getenv('PASSWORD')
        database = os.getenv('DATABASE')
        app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{username}:{password}@localhost:5432/{database}"
        db.init_app(app)

    def create_all(self):
        db.create_all()

    def execute(self, query, params=None):
        result = self.db.engine.execute(query, params)
        return result

    def add_and_commit(self, object):
        db.session.add(object)
        db.session.commit()

    def get_all_videos_path(self):
        videos = models.videos.query.all()
        results = [video.video_path for video in videos]
        return results

    def get_video_path(self, id):
        video = models.videos.query.get(id)
        return video.video_path

    def get_video_key(self, id):
        video = models.videos.query.get(id)
        return video.name

    def get_frames_by_video_id(self, video_id):
        frames = models.frames.query.all()
        filtered_frames = list(filter(lambda frame: (
            frame.video_id == int(video_id)), frames))
        return filtered_frames

    def get_all_frames_path(self, video_id):
        frames = self.get_frames_by_video_id(video_id)
        results = [frame.frame_path for frame in frames]
        return results

    def get_frame_path(self, video_id, frame_index):
        frames = self.get_frames_by_video_id(video_id)
        results = list(filter(lambda frame: (
            frame.index == int(frame_index)), frames))
        return results[0].frame_path

    def get_tagged_frames(self, video_id):
        frames = self.get_frames_by_video_id(video_id)
        results = list(filter(lambda frame: (
            self.is_frame_tagged(frame.metadata_id)), frames))
        return results

    def is_frame_tagged(self, metadata_id):
        metadata = models.metadata.query.get(metadata_id)
        return metadata.tag

    def close(self):
        db.session.close()
