import os
import openai
from datetime import datetime
from pydub import AudioSegment
from pydub import AudioSegment
import glob
from dotenv import load_dotenv

load_dotenv()

# OpenAI APIキーを設定
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

# テキストファイルを統合する関数
def merge_text_files(directory, output_folder):
    # 指定したディレクトリ内の全てのテキストファイルを取得
    os.chdir(directory)
    files = glob.glob("*_part*.txt")

    # ファイルごとの固有名称を管理する辞書
    merged_content = {}

    for file in files:
        # ファイル名から固有名称を取得（"_part"より前の部分）
        unique_name = file.split('_part')[0]

        # ファイル内容を読み込み、辞書に追加
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            if unique_name in merged_content:
                merged_content[unique_name].append(content)
            else:
                merged_content[unique_name] = [content]

    # 統合した内容を指定された出力フォルダに新しいファイルとして書き込む
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for unique_name, contents in merged_content.items():
        output_file = os.path.join(output_folder, f"{unique_name}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(contents))

    print("統合が完了しました。")

# outputフォルダ名を生成
def get_folder_name(base_path, folder_name):
    """指定のフォルダ名とインデックスを元に新しいフォルダを生成する
    
    Args:
        base_path (str): フォルダを作成するベースパス
        folder_name (str): 操作対象のフォルダ名
        
    Returns:
        str: 生成されたフォルダのパス
    """
    today = datetime.now().strftime("%Y-%m-%d")  # 今日の日付を取得
    index = 0
    while True:
        new_folder_name = f"{today}_{folder_name}_{index}"
        new_folder_path = os.path.join(base_path, new_folder_name)
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
            return new_folder_path
        index += 1

# 指定したフォルダ内の全ての.m4aファイルを取得
def get_m4a_files(folder_path):
    return [f for f in os.listdir(folder_path) if f.endswith('.m4a')]

# ファイルを分割する関数
def split_audio(file_path, output_folder, chunk_size_mb=20):
    audio = AudioSegment.from_file(file_path, format="m4a")
    chunk_size = chunk_size_mb * 1024 * 1024  # MBからバイトに変換
    duration_ms = len(audio)
    chunk_duration_ms = (chunk_size * 8) / (audio.frame_rate * audio.frame_width * audio.channels) * 1000  # チャンクの長さ（ミリ秒）を計算

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    start_ms = 0
    part_idx = 1

    while start_ms < duration_ms:
        end_ms = min(start_ms + chunk_duration_ms, duration_ms)
        chunk = audio[start_ms:end_ms]
        chunk.export(os.path.join(output_folder, f"{base_name}_part{part_idx}.m4a"), format="mp4")
        start_ms = end_ms
        part_idx += 1


# 音声をテキスト化する関数
def transcribe_audio(audio_file_path: str, output_directory: str, model: str = "whisper-1") -> str:
    print(f"音声ファイルをテキスト化しています: {audio_file_path}")
    with open(audio_file_path, "rb") as audio_file:
        transcript = openai.audio.transcriptions.create(
            model=model,
            file=audio_file,
            language="ja"  # 言語を日本語に指定
        )
    print("音声ファイルのテキスト化が完了しました")
        # テキストファイルとして保存
    base_filename = os.path.basename(audio_file_path)
    text_filename = os.path.splitext(base_filename)[0] + ".txt"
    text_file_path = os.path.join(output_directory, text_filename)
    with open(text_file_path, "w", encoding="utf-8") as text_file:
        text_file.write(transcript.text)
    print(f"テキストファイルとして保存しました: {text_file_path}")

    return transcript.text

# ChatGPT 4o miniを使用して応答を生成する関数
def generate_response(stance: str, model: str = "gpt-4o") -> str:
    print(f"ChatGPT-{model}を使用して応答を生成しています")
    response = openai.chat.completions.create(
      model=model,
      messages=[
        {"role": "system", "content": "あなたは書記官です。人の実際の会話内容を全て網羅した完全な議事録を執筆する専門家です。"},
        {"role": "user", "content": "会話内容をもとに、会議中に出てきた全ての情報を必ず全く抜け漏れの無いようにまとめた議事録を書いてください。全てのトピックごとの全ての話題と、ネクストアクションについて読みやすくまとめてください。文字数はどれだけ多くなっても構いません。"+stance},
      ]
    )
    print(f"応答が生成されました: {response.choices[0].message.content}")
    return response.choices[0].message.content

# ディレクトリ内のすべての音声ファイルをテキスト化する関数
def transcribe_all_audio_files(directory_path: str):
    for filename in os.listdir(directory_path):
        if filename.endswith(".m4a"):  # 対象の音声ファイル形式を指定
            file_path = os.path.join(directory_path, filename)
            transcribe_audio(file_path, directory_path)

# テキストをファイルに保存する関数
def save_text_to_file(text, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(text)

# 指定したフォルダ内の全ての.txtファイルを取得
def get_txt_files(folder_path):
    return [f for f in os.listdir(folder_path) if f.endswith('.txt')]

# ファイルからテキストを読み込む関数
def read_text_from_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        return "指定されたファイルが見つかりません。"
    except Exception as e:
        return f"エラーが発生しました: {e}"

# メイン処理
if __name__ == "__main__":
    input_path = "input_files"  # ここに元の.m4aファイルが入っているフォルダのパスを指定
    output_parent_folder="gijiroku_output"
    # 音声ファイルを20MBごとに分割する。
    chukei_folder=get_folder_name(output_parent_folder,"chukei")
    output_folder=get_folder_name(output_parent_folder,"output")

    print(f"分割したファイルの出力先フォルダ: {chukei_folder}")
    m4a_files = get_m4a_files(input_path)
    print("音声ファイルを20MBごとに分割しています...")
    for m4a_file in m4a_files:
        split_audio(os.path.join(input_path, m4a_file), chukei_folder)
    print(f"音声ファイルの分割が完了し、{chukei_folder}に保存されました。")
    
    # 使用例
    print("分割された音声ファイルをそれぞれテキスト化しています...")
    transcription=transcribe_all_audio_files(chukei_folder)
    print("音声ファイルのテキスト化が完了しました。")
    print(f"テキストファイルを統合します。")
    stance=f"会話内容は以下の通りです。\n{transcription}"
    merge_text_files(chukei_folder,output_folder)
    print(f"テキストファイルの統合が完了し、出力先フォルダ: {output_folder}に格納しました。")

    txt_files=get_txt_files(output_folder)
    
    for txt_file in txt_files:       
        txt_file = os.path.join(output_folder, txt_file)
        print(f"テキストファイル '{txt_file}' を読み込みます。")
        file_content = read_text_from_file(txt_file)
        print(f"file_content: {file_content}")
        print("OpenAI APIを使用して議事録を作成します。: '{file_content}'")
        stance=f"会話内容は以下の通りです。\n{file_content}"
        summary=generate_response(stance)
        save_text_to_file(summary, f"{output_folder}\\_summary.txt")
    print(f"全ての議事録の作成が完了し、{output_folder}に格納されました。")



