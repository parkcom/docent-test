import base64
import io
import os
import re

import streamlit as st
from openai import OpenAI, api_key
from PIL import Image


def describe(client, url):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "이 이미지에 대해서 아주 자세히 묘사해줘.",
                    },
                    {"type": "image_url", "image_url": {"url": url}},
                ],
            }
        ],
        max_tokens=1024,
    )
    return response.choices[0].message.content


def TTS(client, response):
    # TTS를 활용하여 만든 음성을 파일로 저장.
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="alloy",
        input=response,
    ) as response:
        filename = "audio.mp3"
        response.stream_to_file(filename)

    with open(filename, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        # HTML 문법을 사용하여 자동으로 음원을 재생하는 코드를 작성
        # 스트림릿에서 HTML을 사용할 수 있는 st.markdown을 활용
        md = f"""
<audio autoplay="True">
    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
</audio>
"""
        st.markdown(md, unsafe_allow_html=True)
    os.remove(filename)


def main():
    with st.sidebar:
        openai_apikey = st.text_input(
            "OpenAI API Key", placeholder="Enter your OpenAI API Key", type="password"
        )

        if openai_apikey:
            st.session_state["OPENAI_API_KEY"] = openai_apikey

        st.markdown("---")

    try:
        if st.session_state["OPENAI_API_KEY"]:
            client = OpenAI(api_key=st.session_state["OPENAI_API_KEY"])

    except KeyError:
        st.error("OpenAI API Key를 입력하세요.")
        return

    st.image("ai.png", width=200)
    st.title("이미지를 해설해드립니다.")

    img_file_buffer = st.file_uploader("이미지 파일 업로드", type=["jpg", "jpeg"])

    if img_file_buffer is not None:
        image = Image.open(img_file_buffer)

        st.image(image, caption="업로드된 이미지", use_container_width=True)

        buffered = io.BytesIO()
        image.save(buffered, format="PNG")

        img_base64 = base64.b64encode(buffered.getvalue())

        img_base64_str = img_base64.decode("utf-8")

        image = f"data:image/png;base64,{img_base64_str}"

        text = describe(client, image)
        st.info(text)

        TTS(client, text)


if __name__ == "__main__":
    main()
