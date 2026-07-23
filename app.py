import streamlit as st
import os
import tempfile
import PIL.Image

# Pillow 에러 방지 패치
if not hasattr(PIL.Image, 'Resampling'):
    PIL.Image.Resampling = PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS

try:
    # MoviePy 2.x 최신 버전 임포트 (vfx, afx 포함)
    from moviepy import ImageClip, VideoFileClip, concatenate_videoclips, AudioFileClip, vfx, afx
except ImportError:
    st.error("엔진 설치 마무리 중... 1분 후 새로고침 해주세요.")
    st.stop()

st.set_page_config(page_title="비요일 프로", page_icon="☔")
st.title("☔ 비요일 숏폼 제작소 (Final)")

def process_item(file):
    ext = os.path.splitext(file.name)[1].lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as t:
        t.write(file.read())
        if ext in ['.mp4', '.mov']:
            # 최신 버전은 resized(width=1080) 사용
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
bgm = st.file_uploader("배경음악(MP3)", type=['mp3'])

if st.button("✨ 영상 제작"):
    if files and logo:
        with st.spinner('블랙 화면 제거 및 오디오 페이드 적용 중...'):
            try:
                processed_clips = []
                for i, f in enumerate(files):
                    clip = process_item(f)
                    if i == 0:
                        # 첫 장면: 시작 블랙 방지 (페이드 인 없이 끝만 페이드 아웃)
                        clip = clip.with_effects([vfx.CrossFadeOut(0.5)])
                    else:
                        # 중간 장면들: 앞뒤 부드럽게 겹침
                        clip = clip.with_effects([vfx.CrossFadeIn(0.5), vfx.CrossFadeOut(0.5)])
                    processed_clips.append(clip)
                
                # 브랜드 로고 엔딩 (줌 인 효과)
                l_clip = process_item(logo).with_duration(4.0).with_effects([
                    vfx.CrossFadeIn(0.5),
                    vfx.Resize(lambda t: 1 + 0.02 * t)
                ])
                processed_clips.append(l_clip)
                
                # 영상 합치기 (0.5초씩 겹침)
                final = concatenate_videoclips(processed_clips, method="compose", padding=-0.5)
                
                # 오디오 처리 (MoviePy 2.x afx 전용 문법)
                if bgm:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mt:
                        mt.write(bgm.read())
                        audio = AudioFileClip(mt.name).with_duration(final.duration)
                        # 최신 버전 전용 오디오 페이드 인/아웃 효과 적용
                        audio = audio.with_effects([
                            afx.AudioFadeIn(1.0),
                            afx.AudioFadeOut(2.0)
                        ])
                        final = final.with_audio(audio)
                
                output_name = "biyoil_perfect_final.mp4"
                final.write_videofile(output_name, fps=24, codec="libx264", audio_codec="aac")
                
                st.video(output_name)
                st.success("🎉 완벽한 영상이 완성되었습니다!")
            except Exception as e:
                st.error(f"제작 중 에러 발생: {str(e)}")
    else:
        st.error("파일을 모두 올려줘!")
