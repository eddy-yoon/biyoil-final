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
st.title("☔ 비요일 숏폼 제작소 (BGM 페이드 적용)")

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
        with st.spinner('음악에 페이드 효과를 입혀 제작 중입니다...'):
            try:
                processed_clips = []
                for i, f in enumerate(files):
                    clip = process_item(f)
                    if i == 0:
                        # 첫 장면 블랙 방지: 페이드 인 없이 바로 시작
                        clip = clip.with_effects([vfx.CrossFadeOut(0.5)])
                    else:
                        clip = clip.with_effects([vfx.CrossFadeIn(0.5), vfx.CrossFadeOut(0.5)])
                    processed_clips.append(clip)
                
                # 로고 엔딩 (줌 인 효과)
                l_clip = process_item(logo).with_duration(4.0).with_effects([
                    vfx.CrossFadeIn(0.5),
                    vfx.Resize(lambda t: 1 + 0.02 * t)
                ])
                processed_clips.append(l_clip)
                
                # 영상 합치기
                final = concatenate_videoclips(processed_clips, method="compose", padding=-0.5)
                
                # 오디오 처리 (페이드 인/아웃 적용)
                if bgm:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mt:
                        mt.write(bgm.read())
                        audio = AudioFileClip(mt.name).with_duration(final.duration)
                        # 오디오 시작 1초 페이드 인, 끝 2초 페이드 아웃
                        audio = audio.audio_fadein(1.0).audio_fadeout(2.0)
                        final = final.set_audio(audio)
                
                output_filename = "biyoil_final_audio.mp4"
                final.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")
                
                st.video(output_filename)
                st.success("🎉 음악까지 완벽한 영상이 완성되었습니다!")
            except Exception as e:
                st.error(f"에러 발생: {str(e)}")
    else:
        st.error("파일들을 올려줘!")
