import io
import cv2
import models
import S3Manger
import DBManager
import given_functions
from dotenv import load_dotenv
from flask import Flask, request

load_dotenv()
app = Flask(__name__)
db = DBManager.DBManager(app)
s3 = S3Manger.S3Manager()


def create_frame_metadate(capture, video_id):
    frame_index = 0
    success = 1

    while success:
        success, image = capture.read()
        if (success):
            frame_metadate_handler(frame_index, image, video_id)
        else:
            break
        frame_index += 1

    capture.release()


def save_video_s3(video_path, object_name):
    key = f'{object_name}.mp4'
    s3.upload_file(video_path, 'sapir-videos', key)
    return s3.get_url('sapir-videos', key)


def frame_metadate_handler(frame_index, frame, video_id):
    key = f'{frame_index}.jpg'
    url = save_img_s3(frame, key)
    save_frame_metadata_db(frame, url, frame_index, video_id)


def save_img_s3(frame, key):
    data = io.BytesIO(frame)
    s3.upload_fileobj(data, 'sapir-images', key)
    return s3.get_url('sapir-images', key)


def save_frame_metadata_db(frame, url, frame_index, video_id):
    fov, azimuth, elevation = given_functions.generate_metadata(frame)
    db_metadata = models.metadata(tag=given_functions.is_frame_tagged(
        frame), fov=fov, azimuth=azimuth, elevation=elevation)
    db.add_and_commit(db_metadata)
    db_frame = models.frames(frame_path=url, index=frame_index,
                             metadata_id=db_metadata.id, video_id=video_id)
    db.add_and_commit(db_frame)


@app.route('/video')
def post_video():
    try:
        path = request.args.get('path')
        video = cv2.VideoCapture(path)
        position_name = path.split('/').pop().split('_')[0]
        url = save_video_s3(path, position_name)
        frames_num = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        db_video = models.videos(name=position_name, video_path=url,
                                 frames_num=frames_num)
        db.add_and_commit(db_video)
        create_frame_metadate(video, db_video.id)

        return 'post video'
    except Exception as e:
        print(e)


@app.route('/all_videos_path')
def get_all_videos_path():
    return db.get_all_videos_path()


@app.route('/video_path/<video_id>')
def get_video_path(video_id):
    return db.get_video_path(video_id)


@app.route('/all_frames_path/<video_id>')
def get_all_frames_path(video_id):
    return db.get_all_frames_path(video_id)


@app.route('/frame_path/<video_id>/<frame_index>')
def get_frame_path(video_id, frame_index):
    return db.get_frame_path(video_id, frame_index)


@app.route('/download_video/<video_id>')
def download_video(video_id):
    key = f'{db.get_video_key(video_id)}.mp4'
    s3.download_file(key, 'sapir-videos')
    return 'download video'


@app.route('/download_tagged_frames/<video_id>')
def download_tagged_frames(video_id):
    frames = db.get_tagged_frames(video_id)
    for frame in frames:
        key = f'{frame.index}.jpg'
        s3.download_file(key, 'sapir-images')
    return 'download tagged frames'


def main():
    with app.app_context():
        db.create_all()

    app.run(debug=True)


if __name__ == "__main__":
    main()
