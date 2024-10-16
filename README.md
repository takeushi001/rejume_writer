## 📖 概要



このプロジェクトは、音声ファイルを自動でテキスト化し、議事録などのドキュメントとして出力するPythonスクリプトです。音声ファイルを特定のサイズで分割し、OpenAIのAPIを活用してテキストに変換し、それを統合して最終的なアウトプットとして保存します。特に、会議の議事録やインタビューのテキスト化など、長い音声を効率よく処理することを目的としています。



## ✨ 主な機能



- **音声ファイルの分割**：20MBごとに音声ファイルを分割し、処理しやすいサイズにします。

- **音声のテキスト化**：OpenAIのWhisperモデルを使用して、音声をテキストに変換します。

- **テキストの統合**：複数のテキストファイルを統合し、一つのファイルとして出力します。

- **議事録生成**：ChatGPTを使用して、会話内容を元に議事録を生成し、読みやすくまとめます。



## 🛠️ 必要な環境



- Python 3.8以上

- 以下のPythonパッケージが必要です：

    - `openai`

    - `pydub`

    - `dotenv`

    - `tqdm`

- 環境変数ファイル（.env）にOpenAIのAPIキーを設定する必要があります。



## 🚀 インストール方法



1. リポジトリをクローンします：

    

    ```

    git clone <repository-url>

    ```

    

2. 必要なライブラリをインストールします：

    

    ```

    pip install -r requirements.txt

    ```

    

3. `.env`ファイルを作成し、OpenAIのAPIキーを設定します：

    

    ```

    OPENAI_API_KEY=your_openai_api_key

    ```

    



## ▶️ 使用方法



1. `input_files` フォルダに処理したい `.m4a` 音声ファイルを配置します。

2. スクリプトを実行します：

    

    ```

    python audio_transcription_tool.py

    ```

    

3. 分割された音声ファイルが `gijiroku_output/chukei` フォルダに保存され、テキスト化されたファイルが `gijiroku_output/output` フォルダに保存されます。



## 📚 主な処理の流れ



1. **🎧 音声ファイルの分割**

    - `split_audio()` 関数を使用して、音声ファイルを20MBごとに分割します。

    - 以下は、音声ファイルを分割するコードの抜粋です：

        

        ```

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

        ```

        

    - この関数は、大きな音声ファイルを分割し、各チャンクを処理しやすいサイズにするために使用されます。

2. **📝 音声のテキスト化**

    - `transcribe_audio()` 関数で、分割された音声ファイルをテキストに変換します。OpenAIのWhisper APIを利用して、精度の高い音声認識を実現しています。

    - 以下は、音声をテキスト化するコードの抜粋です：

        

        ```

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

        ```

        

    - この関数は、音声ファイルをテキスト化し、その結果をファイルに保存します。

3. **🗂️ テキストの統合**

    - `merge_text_files()` 関数で、分割されたテキストファイルを一つに統合します。

    - 以下は、テキストファイルを統合するコードの抜粋です：

        

        ```

        def merge_text_files(directory, output_folder):

            os.chdir(directory)

            files = glob.glob("*_part*.txt")

        

            merged_content = {}

        

            for file in files:

                unique_name = file.split('_part')[0]

                with open(file, 'r', encoding='utf-8') as f:

                    content = f.read()

                    if unique_name in merged_content:

                        merged_content[unique_name].append(content)

                    else:

                        merged_content[unique_name] = [content]

        

            if not os.path.exists(output_folder):

                os.makedirs(output_folder)

        

            for unique_name, contents in merged_content.items():

                output_file = os.path.join(output_folder, f"{unique_name}.txt")

                with open(output_file, 'w', encoding='utf-8') as f:

                    f.write('\n'.join(contents))

        

            print("統合が完了しました。")

        ```

        

    - この関数は、分割されたテキストファイルを結合し、一つの統合されたテキストファイルを生成します。

4. **📝 議事録生成**

    - `generate_response()` 関数で、統合されたテキストを基に議事録を生成します。

    - この関数は、ChatGPTを利用して、会話内容を読みやすい議事録形式にまとめます。

    - 以下は、議事録を生成するコードの抜粋です：

        

        ```

        def generate_response(stance: str, model: str = "gpt-4o") -> str:

            print(f"ChatGPT-{model}を使用して応答を生成しています")

            response = openai.chat.completions.create(

              model=model,

              messages=[

                {"role": "system", "content": "あなたは書記官です。人の実際の会話内容を全て縦約した完全な議事録を執筆する専門家です。"},

                {"role": "user", "content": "会話内容をもとに、会議中に出てきた全ての情報を必ず全く抜け漏れの無いようにまとめた議事録を書いてください。全てのトピックごとの全ての話題と、ネクストアクションについて読みやすくまとめてください。文字数はどれだけ多くなっても構いません。" + stance},

              ]

            )

            print(f"応答が生成されました: {response.choices[0].message.content}")

            return response.choices[0].message.content

        ```

        

    - この関数は、音声から抽出されたテキストを基に、重要な内容をまとめた議事録を自動的に生成します。



## 💡 ユースケースシナリオ



1. **会議の議事録作成**

    - 重要な会議の音声を録音し、このツールを使って自動的に議事録を生成することができます。これにより、会議に参加できなかったメンバーに対して、迅速かつ正確に情報を共有することが可能です。

2. **インタビューの文字起こし**

    - インタビューの音声データをテキスト化し、後から簡単に内容を確認したり、分析したりすることができます。特に、複数のインタビューをまとめる際に便利です。

3. **ウェビナーや講演のテキスト化**

    - ウェビナーや講演など、長時間の音声コンテンツをテキスト化し、参加者へのフォローアップ資料として提供することができます。

4. **法的な記録の作成**

    - 会議や証言の音声記録をテキストに変換し、法的な記録や証拠として使用することができます。

5. **顧客サポートの記録**

    - 顧客との通話内容を記録し、サポート内容をテキスト化することで、顧客対応の品質向上やトラブル防止に役立てることができます。



## 📄 サンプル出力



音声ファイルを分割し、各ファイルをテキスト化、その後に統合して最終的な議事録を生成します。例えば、会議内容をすべて網羅した形式の議事録を自動で生成するため、会議に参加できなかったメンバーへの共有や、内容の復習に最適です。



## 🔧 今後の改善点



- **GUIの追加**：より使いやすくするため、GUIインターフェースの追加を検討しています。

- **他言語対応**：現状は日本語のみに対応していますが、他言語への対応も計画中です。

- **リアルタイム処理**：将来的には、リアルタイムでの音声認識とテキスト化も可能にしたいと考えています。



## ⚠️ 注意点



- OpenAIのAPIを利用しているため、APIキーの管理には十分に注意してください。

- 音声ファイルの品質によっては、テキスト化の精度が異なる場合があります。



## 📜 ライセンス



MITライセンスのもとで公開されています。自由にご利用ください。



## 🤝 コントリビューション



このプロジェクトへの貢献を歓迎します。バグ報告や機能改善の提案など、お気軽にPull Requestを送ってください。



## 📧 お問い合わせ



何か質問があれば、プロジェクトのIssueページからお気軽にお問い合わせください。
