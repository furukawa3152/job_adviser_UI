import streamlit as st
from openai import OpenAI
from docx import Document
from docx.shared import Pt, RGBColor
import os
# OpenAI APIキーを設定
api_key = ""

st.title("AIにきいてみよう。")
# ユーザー名の入力フォーム
user_name = st.text_input("なまえをいれてね:", key="user_name")
school_year = st.selectbox("がくねんをおしえてね", ("1年生", "2年生", "3年生", "4年生", "5年生", "6年生"))
# セッションステートの初期化
if 'messages' not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": f"あなたは小学{school_year}に対して様々な職業を教えてくれるAIです。質問に対し、小学{school_year}の子供に分かる言葉で回答してください。回答相手の名前は{user_name}です。名前を呼びながら回答してあげてください。小学1年生は7歳、6年生は12歳です。年齢に応じた漢字の使用や言葉遣いを気がけて下さい。"}]
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = ""

if user_name != "":
    # 会話履歴を表示（最初のプロンプトをスキップ）
    for i, message in enumerate(st.session_state.messages):
        if i == 0 and message["role"] == "system":
            continue  # 最初のプロンプトをスキップ
        if message["role"] == "user":
            st.write(f"{message['content']}")
        else:
            st.write(f"AI: {message['content']}")

    # テキストボックスの値を保持するための一時変数
    temp_input = st.text_input("しつもんを入れよう:", key="temp_user_input", value="")

    # 送信ボタンが押された場合の処理
    # 送信ボタンが押された場合の処理
    if st.button("きいてみる"):
        if temp_input and user_name:
            # ユーザーのメッセージを会話履歴に追加
            user_message = f"{user_name}: {temp_input}"
            st.session_state.messages.append({"role": "user", "content": user_message})

            # OpenAI APIを呼び出して応答を生成
            try:
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    messages=st.session_state.messages,
                    model="gpt-4o",
                )
                assistant_message = response.choices[0].message.content
                # OpenAIの応答を会話履歴に追加
                st.session_state.messages.append({"role": "assistant", "content": assistant_message})
                # 会話履歴を更新
                st.session_state.conversation_history += f"{user_message}\nAI: {assistant_message}\n"

            except Exception as e:
                st.error(f"Error: {str(e)}")

            # 入力フィールドをクリアするために一時変数をリセット
            st.experimental_rerun()
    # リセットボタンの処理
    if st.button("はじめから"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.experimental_rerun()
    # 更新された会話のやり取りを表示
    st.write("Conversation History:")
    st.text(st.session_state.conversation_history)

    if st.button("保存"):

        # テンプレートとなるWordファイルの読み込み
        template_path = 'template.docx'
        doc = Document(template_path)

        # テキストデータの挿入位置を特定してテキストを挿入
        for paragraph in doc.paragraphs:
            if 'PLACEHOLDER' in paragraph.text:
                paragraph.text = paragraph.text.replace('PLACEHOLDER', st.session_state.conversation_history)
            # フォント指定
            for run in paragraph.runs:
                run.font.name = 'メイリオ'  # フォントの種類
                run.font.size = Pt(12)  # フォントサイズ
        # 新しいWordファイルとして保存
        output_path = f'{user_name}さん{school_year}.docx'
        doc.save(output_path)

        print(f"New Word document saved as {output_path}")