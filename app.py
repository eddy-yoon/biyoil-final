import streamlit as st
import os
import tempfile
import PIL.Image

if not hasattr(PIL.Image, 'Resampling'):
    PIL.Image.Resampling = PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

try:
    from moviepy import ImageClip, VideoFileClip, concatenate_videoclips, AudioFileClip, vfx
except ImportError:
    st.error("엔진 설치 마무리 중... 1분 후 새로고침 해주세요.")
    st.stop()

st.set_page_config(page_title="비요일 프로", page_icon="☔")
st.title("☔ 비요일 숏폼 제작소 (BGM 페이드 완벽 대응)")

def process_item(file):
    ext = os.path.splitext(file.name)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as t:
        t.write(file.read())
        if ext in ['.mp4', '.mov']:
            clip = VideoFileClip(t.name).without_audio().resized(width=1080)
            if clip.h > 1920:
                clip = clip.cropped(y_center=clip.h/2, height=1920)
        else:
            img = PIL.Image.open(t.name).convert("RGB")
            img = img.resize((1080, 1920), PIL.Image.ANTIALIAS)
            img.save(t.name + ".png")
            clip = ImageClip(t.name + ".png").with_duration(2.0)
    return clip.with_fps(24)

files = st.file_uploader("사진/영상 업로드", accept_multiple_files=True, type=['jpg','png','mp4','mov'])
logo = st.file_uploader("로고 업로드", type=['jpg','png'])
bgm = st.file_uploader("배경음악(MP3) - Happy Day 추천", type=['mp3'])

if st.button("✨ 영상 제작"):
    if files and logo:
        with st.spinner('음악 페이드 인/아웃 적용 중...'):
            try:
                processed_clips = []
                for i, f in enumerate(files):
                    clip = process_item(f)
                    if i == 0:
                        # 첫 장면 블랙 방지
                        clip = clip.with_effects([vfx.CrossFadeOut(0.5)])
                    else:
                        clip = clip.with_effects([vfx.CrossFad
