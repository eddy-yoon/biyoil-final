import streamlit as st
import os
import tempfile
import PIL.Image

# [필독] 최신 환경 에러 방지 패치
if not hasattr(PIL.Image, 'Resampling'):
    PIL.Image.Resampling = PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

try:
    from moviepy.editor import ImageClip, VideoFileClip, concatenate_videoclips, AudioFileClip, vfx
except ImportError:
    st.error("설치 중입니다. 1~2분만 기다린 후 새로고침 해주세요.")
    st.stop()

st.set_page_config(page_title="비요일 프로", page_icon="☔")
st.title("☔ 비요일 숏폼 제작소 (최종)")

def process_item(file):
    ext = os.path.splitext(file.name)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as t:
        t.write(file.read())
        if ext in ['.mp4', '.mov']:
            clip = VideoFileClip(t.name).without_audio().resize(width=1080)
            if clip.height > 1920: clip = clip.crop(y_center=clip.height/2, height=1920)
        else:
            img = PIL.Image.open(t.name).convert("RGB")
            img = img.resize((1080, 1920), PIL.Image.ANTIALIAS)
            img.save(t.name + ".png")
            clip = ImageClip(t.name + ".png").set_duration(2.0)
    return clip.set_fps(24).crossfadein(0.5).crossfadeout(0.5)

files = st.file_uploader("사진/영상 업로드", accept_multiple_files=True, type=['jpg','png','mp4','mov'])
logo = st.file_uploader("로고 업로드", type=['jpg','png'])
bgm = st.file_uploader("배경음악(MP3)", type=['mp3'])

if st.button("✨ 영상 제작"):
    if files and logo:
        with st.spinner('영상을 굽는 중...'):
            try:
                clips = [process_item(f) for f in files]
                l_clip = process_item(logo).set_duration(4.0).fx(vfx.resize, lambda t: 1 + 0.02*t)
                clips.append(l_clip)
                final = concatenate_videoclips(clips, method="compose", padding=-0.5)
                if bgm:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mt:
                        mt.write(bgm.read())
                        final = final.set_audio(AudioFileClip(mt.name).set_duration(final.duration))
                final.write_videofile("out.mp4", fps=24, codec="libx264", audio_codec="aac")
                st.video("out.mp4")
            except Exception as e: st.error(f"에러: {e}")
