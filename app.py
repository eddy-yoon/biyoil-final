import streamlit as st
import os
import tempfile
import PIL.Image

# 최신 Pillow 에러 방지
if not hasattr(PIL.Image, 'Resampling'):
    PIL.Image.Resampling = PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

try:
    # MoviePy 2.x 최신 버전 임포트
    from moviepy import ImageClip, VideoFileClip, concatenate_videoclips, AudioFileClip, vfx
except ImportError:
    st.error("엔진 설치 마무리 중입니다. 1분만 기다린 후 새로고침 해주세요.")
    st.stop()

st.set_page_config(page_title="비요일 프로", page_icon="☔")
st.title("☔ 비요일 숏폼 제작소 (v2.2.1 최적화)")

def process_item(file):
    ext = os.path.splitext(file.name)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as t:
        t.write(file.read())
        if ext in ['.mp4', '.mov']:
            # 최신 버전은 .h, .w 를 사용함
            clip = VideoFileClip(t.name).without_audio().resized(width=1080)
            if clip.h > 1920:
                clip = clip.cropped(y_center=clip.h/2, height=1920)
        else:
            img = PIL.Image.open(t.name).convert("RGB")
            img = img.resize((1080, 1920), PIL.Image.ANTIALIAS)
            img.save(t.name + ".png")
            clip = ImageClip(t.name + ".png").with_duration(2.0)
    
    # 페이드 효과 적용 (최신 버전 문법)
    return clip.with_fps(24).with_effects([vfx.CrossFadeIn(0.5), vfx.CrossFadeOut(0.5)])

files = st.file_uploader("사진/영상 업로드", accept_multiple_files=True, type=['jpg','png','mp4','mov'])
logo = st.file_uploader("로고 업로드", type=['jpg','png'])
bgm = st.file_uploader("배경음악(MP3)", type=['mp3'])

if st.button("✨ 영상 제작"):
    if files and logo:
        with st.spinner('영상을 굽는 중... (약 1분 소요)'):
            try:
                # 1. 메인 클립들 처리
                clips = [process_item(f) for f in files]
                
                # 2. 로고 엔딩 처리 (4초, 서서히 확대 효과)
                l_clip = process_item(logo).with_duration(4.0).with_effects([vfx.Resize(lambda t: 1 + 0.02*t)])
                clips.append(l_clip)
                
                # 3. 영상 합치기 (0.5초씩 겹쳐서 부드럽게)
                final = concatenate_videoclips(clips, method="compose", padding=-0.5)
                
                # 4. 음악 입히기
                if bgm:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mt:
                        mt.write(bgm.read())
                        audio = AudioFileClip(mt.name).with_duration(final.duration)
                        final = final.with_audio(audio)
                
                # 5. 최종 파일 추출
                output_filename = "biyoil_final.mp4"
                final.write_videofile(output_filename, fps=24, codec="libx264", audio_codec="aac")
                
                st.video(output_filename)
                st.success("🎉 드디어 완성! 영상을 확인하고 저장하세요.")
            except Exception as e:
                st.error(f"제작 중 에러 발생: {str(e)}")
    else:
        st.error("파일을 모두 올려줘!")
