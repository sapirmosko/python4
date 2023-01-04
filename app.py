import os
import cv2
import boto3
import models
import given_functions
from dotenv import load_dotenv
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
username = os.getenv('USER_NAME')
password = os.getenv('PASSWORD')
database = os.getenv('DATABASE')

app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{username}:{password}@localhost:5432/{database}"
db = SQLAlchemy(app)

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('REGION')
)


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


def save_img_s3(frame, frame_path):
    cv2.imwrite('image.jpg', frame)
    with open('image.jpg', 'rb') as f:
        s3.upload_fileobj(f, 'sapir-bucket-2', frame_path)

    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': 'sapir-bucket-2', 'Key': frame_path}
    )

    return url


def frame_metadate_handler(frame_index, frame, video_id):
    frame_path = f'{frame_index}.jpg'
    url = save_img_s3(frame, frame_path)
    save_frame_metadata_db(frame, url, frame_index, video_id)


def save_frame_metadata_db(frame, url, frame_index, video_id):
    fov, azimuth, elevation = given_functions.generate_metadata(frame)
    db_metadata = models.metadata(tag=given_functions.is_frame_tagged(
        frame), fov=fov, azimuth=azimuth, elevation=elevation)
    db.session.add(db_metadata)
    db.session.commit()
    db_frame = models.frames(frame_path=url, index=frame_index,
                      metadata_id=db_metadata.id, video_id=video_id)
    db.session.add(db_frame)
    db.session.commit()


@app.route('/video')
def post_video():
    path = request.args.get('path')
    position_name = path.split('/').pop().split('_')[0]
    video = cv2.VideoCapture(path)
    frames_num = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    db_video = models.videos(name=position_name, video_path=path,
                      frames_num=frames_num)
    db.session.add(db_video)
    db.session.commit()
    create_frame_metadate(video, db_video.id)
    return 'post video'


def main():
    with app.app_context():
        db.create_all()
    app.run(debug=True)


if __name__ == "__main__":
    main()
