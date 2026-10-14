# -*- coding: utf-8 -*-
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def build_excel():
    wb = openpyxl.Workbook()
    default_sheet = wb.active

    # Fonts
    FONT_FAMILY = "Meiryo UI"
    font_title = Font(name=FONT_FAMILY, size=14, bold=True, color="212529")
    font_subtitle = Font(name=FONT_FAMILY, size=10, italic=True, color="495057")
    font_section = Font(name=FONT_FAMILY, size=11, bold=True, color="212529")
    font_tbl_header = Font(name=FONT_FAMILY, size=10, bold=True, color="FFFFFF")
    font_tbl_sub = Font(name=FONT_FAMILY, size=9.5, bold=True, color="FFFFFF")
    font_bold = Font(name=FONT_FAMILY, size=9.5, bold=True, color="212529")
    font_regular = Font(name=FONT_FAMILY, size=9.5, color="212529")
    font_mono = Font(name=FONT_FAMILY, size=9, color="343A40")

    # Fills (Monotone Palette)
    fill_header_dark = PatternFill(start_color="343A40", end_color="343A40", fill_type="solid")  # Dark Charcoal #343A40
    fill_header_slate = PatternFill(start_color="495057", end_color="495057", fill_type="solid") # Slate Gray #495057
    fill_header_section = PatternFill(start_color="CED4DA", end_color="CED4DA", fill_type="solid") # Light Slate Gray #CED4DA
    fill_row_white = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    fill_row_alt = PatternFill(start_color="F8F9FA", end_color="F8F9FA", fill_type="solid")      # Off-white / Soft Gray
    fill_row_highlight = PatternFill(start_color="E9ECEF", end_color="E9ECEF", fill_type="solid") # Subtle light gray

    # Borders (Monotone)
    bd_thin_color = "CED4DA"
    bd_dark_color = "495057"
    thin_border_side = Side(style="thin", color=bd_thin_color)
    thick_bottom_side = Side(style="medium", color=bd_dark_color)
    double_bottom_side = Side(style="double", color=bd_dark_color)

    cell_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    header_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thick_bottom_side)

    # Alignments
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
    align_center = Alignment(horizontal="center", vertical="center", wrap_text=True)
    align_right = Alignment(horizontal="right", vertical="center", wrap_text=True)
    align_header = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Helper function to style a table with dynamic row height calculation
    def format_table(ws, start_row, headers, data, alignments=None, alt_color=True, col_start=2, col_widths=None):
        current_row = start_row
        ws.row_dimensions[current_row].height = 32
        for col_idx, header_text in enumerate(headers, start=col_start):
            cell = ws.cell(row=current_row, column=col_idx, value=header_text)
            cell.font = font_tbl_header
            cell.fill = fill_header_dark
            cell.border = header_border
            cell.alignment = align_header

        current_row += 1
        for r_idx, row_values in enumerate(data):
            # Calculate required lines across all cells in this row
            max_lines = 1
            for c_idx, val in enumerate(row_values):
                val_str = str(val)
                lines_by_break = val_str.count("\n") + 1
                # Estimate line count by character width if width is specified
                est_lines = lines_by_break
                if col_widths and c_idx < len(col_widths):
                    col_w = col_widths[c_idx]
                    # Approx 1 Japanese character = 2 width units, English = 1 unit
                    # Count display width
                    disp_len = sum(2 if ord(ch) > 127 else 1 for ch in val_str.replace("\n", " "))
                    lines_by_len = int(disp_len / (col_w * 1.6)) + 1
                    est_lines = max(lines_by_break, lines_by_len)
                if est_lines > max_lines:
                    max_lines = est_lines

            # Set comfortable row height (approx 16-18pt per line + padding)
            row_height = max(26, min(140, max_lines * 17 + 10))
            ws.row_dimensions[current_row].height = row_height

            fill = fill_row_alt if (r_idx % 2 == 1 and alt_color) else fill_row_white
            for col_idx, val in enumerate(row_values, start=col_start):
                cell = ws.cell(row=current_row, column=col_idx, value=val)
                cell.font = font_regular
                cell.fill = fill
                cell.border = cell_border

                if alignments and col_idx - col_start < len(alignments):
                    cell.alignment = alignments[col_idx - col_start]
                else:
                    cell.alignment = align_left
            current_row += 1
        return current_row

    # =========================================================================
    # SHEET 1: 概要 & 直列並列比較
    # =========================================================================
    ws1 = wb.create_sheet(title="1_概要 & 直列並列比較")
    ws1.views.sheetView[0].showGridLines = True

    # Title Banner
    ws1.merge_cells("B2:F2")
    ws1["B2"] = "【ECSタスク起動順】ADOTサイドカー直列起動 vs 並列起動 徹底比較"
    ws1["B2"].font = font_title
    ws1["B2"].alignment = Alignment(horizontal="left", vertical="center")
    ws1.row_dimensions[2].height = 34

    ws1.merge_cells("B3:F3")
    ws1["B3"] = "〜 起動順序（dependsOn）の有無がもたらすトレース欠落リスクとアーキテクチャ特性の完全対比 〜"
    ws1["B3"].font = font_subtitle
    ws1["B3"].alignment = Alignment(horizontal="left", vertical="center")
    ws1.row_dimensions[3].height = 22

    # Section 1 Header
    ws1.merge_cells("B5:F5")
    ws1["B5"] = "■ 1. コンテナ起動方式ごとの特性比較マトリクス"
    ws1["B5"].font = font_section
    ws1["B5"].fill = fill_header_section
    ws1["B5"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws1.row_dimensions[5].height = 26

    headers_comp = [
        "比較項目",
        "パターンA: 完全直列起動\n(ADOT -> Back -> Front)",
        "パターンB: 完全並列起動\n(依存関係なし / よーいドン)",
        "パターンC: 実務推奨ハイブリッド\n(ADOT[HEALTHY] -> Back -> Front)",
        "技術的詳細・欠落メカニズムの評価"
    ]
    data_comp = [
        [
            "トレース収集の完全性\n(Trace Completeness)",
            "◎ 100% 収集保証\n(欠落リスクゼロ)",
            "× 極めて高い欠落リスク\n(起動初期の数秒〜数十秒消失)",
            "◎ 100% 収集保証\n(初期化から全て捕捉)",
            "ADOTが受信ソケット (4317/4318) を開く前に送信されたスパンは、OSカーネルで即座に拒絶 (RST) または破棄されます。"
        ],
        [
            "タスク全体の起動所要時間\n(Task Startup Latency)",
            "△ 長い\n(各コンテナ起動時間の総和)",
            "○ 最短\n(最も遅いコンテナの起動時間)",
            "○ 実用的な長さ\n(ADOT起動後にアプリが立ち上がる)",
            "直列は安全ですが起動時間が伸びます。ハイブリッドではADOT準備完了後にアプリ群を立ち上げることで安全と速度を両立します。"
        ],
        [
            "起動時 502/503 エラーリスク\n(Early Traffic Failure)",
            "◎ 完全に防止\n(依存先が起動完了してから前段が稼働)",
            "× 多発リスクあり\n(FrontがBackより先に動いて失敗)",
            "◎ 完全に防止\n(Backの健全性を確認してFront起動)",
            "フロントコンテナが先行して外部リクエストを受け付けると、バックエンドが未接続のため 502 Bad Gateway が発生します。"
        ],
        [
            "初回リクエスト / コールドスタート観測",
            "◎ 完全にトレース可能\n(初期DB接続・認証も記録)",
            "× 観測不能（盲目状態）\n(初回アクセスのトレース消失)",
            "◎ 完全にトレース可能\n(起動直後の挙動を完全把握)",
            "コールドスタート時のレイテンシ急増、DB初期コネクションプールの構築遅延など、最も重要な初動トレースが並列では消滅します。"
        ],
        [
            "ECS dependsOn の設定内容",
            "Back: ADOT (HEALTHY)\nFront: Back (HEALTHY)",
            "設定なし (空配列 [])",
            "Back: ADOT (HEALTHY)\nFront: Back (HEALTHY)",
            "条件 (condition) は必ず 'HEALTHY' である必要があります。'START' ではポート未開放のため欠落を防げません。"
        ],
        [
            "ADOT側のヘルスチェック設定",
            "必須\n(ポート 13133 / health_check)",
            "不要 (ただしタスク管理上は非推奨)",
            "必須\n(ポート 13133 / health_check)",
            "ADOTの health_check エクステンションを有効化し、ECSタスク定義の healthCheck でポーリング監視します。"
        ],
        [
            "推奨ユースケース・適用判断",
            "基幹系、金融、マイクロサービス間\n依存関係が強固なシステム",
            "使い捨てバッチ処理、トレース不要な\nスタンドアロンタスク",
            "★ 本番環境のWeb/API全般\n(モダンクラウドアーキテクチャ標準)",
            "本番サービスではトレース欠落と起動時502エラーを絶対に防止するため、パターンC（またはA）が鉄則です。"
        ]
    ]
    aligns_comp = [align_center, align_center, align_center, align_center, align_left]
    widths_comp = [24, 26, 26, 28, 48]
    next_r = format_table(ws1, 6, headers_comp, data_comp, aligns_comp, alt_color=True, col_start=2, col_widths=widths_comp)

    # Section 2 Header
    next_r += 1
    ws1.merge_cells(f"B{next_r}:F{next_r}")
    ws1[f"B{next_r}"] = "■ 2. 小学生にもわかる「学校の学芸会」対比表"
    ws1[f"B{next_r}"].font = font_section
    ws1[f"B{next_r}"].fill = fill_header_section
    ws1[f"B{next_r}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws1.row_dimensions[next_r].height = 26

    headers_meta = [
        "コンテナ名",
        "学芸会での役割",
        "並列起動のとき（よーいドン！）",
        "直列起動のとき（dependsOn）",
        "なぜこの順番が大切なのか？"
    ]
    data_meta = [
        [
            "ADOTサイドカー\n(aws-otel-collector)",
            "ビデオカメラ係・記録係\n(校長先生に提出するビデオを撮る人)",
            "三脚を広げている最中に劇が始まり、\n一番最初のシーンを撮り逃す！",
            "カメラの電源を入れて録画ランプをつけて\n「OKだよ！」と合図を出してから劇が始まる",
            "カメラマンが準備できていないと、劇で何が起きても記録に残らず、後で先生に怒られてしまいます。"
        ],
        [
            "バックエンドコンテナ\n(API / 業務ロジック)",
            "舞台裏の音響・大道具係\n(BGMを鳴らしたり照明をつける人)",
            "司会者から「音鳴らして！」と言われても\nまだアンプの電源が入っておらず音が鳴らない",
            "カメラマンがOKを出してから機材の準備をし、\n音が鳴るようになってから司会者に合図する",
            "裏方が準備できていないと、主役がステージに立っても音が鳴らず、劇が台無しになります。"
        ],
        [
            "フロントエンドコンテナ\n(Web UI / Nginx)",
            "ステージの司会者・主役\n(お客さんの前に立って劇を進める人)",
            "幕が開いてすぐに話し始めるが、音も鳴らず、\nカメラにも映っていない大パニック！",
            "カメラマンも音響係も「全員準備完了！」の\n合図を出してから、堂々と幕を開ける",
            "お客さんを迎える人は一番最後！全員の準備が整ってからドアを開けるのがおもてなしの基本です。"
        ]
    ]
    aligns_meta = [align_center, align_center, align_left, align_left, align_left]
    widths_meta = [24, 26, 32, 34, 36]
    format_table(ws1, next_r + 1, headers_meta, data_meta, aligns_meta, alt_color=True, col_start=2, col_widths=widths_meta)

    # Set Column Widths for Sheet 1
    ws1.column_dimensions["A"].width = 3
    ws1.column_dimensions["B"].width = 24
    ws1.column_dimensions["C"].width = 28
    ws1.column_dimensions["D"].width = 32
    ws1.column_dimensions["E"].width = 34
    ws1.column_dimensions["F"].width = 48

    # =========================================================================
    # SHEET 2: 欠落メカニズム & タイムライン
    # =========================================================================
    ws2 = wb.create_sheet(title="2_欠落メカニズム & タイムライン")
    ws2.views.sheetView[0].showGridLines = True

    ws2.merge_cells("B2:H2")
    ws2["B2"] = "【動作原理】ミリ秒（ms）タイムラインとOSカーネルレベルの欠落メカニズム"
    ws2["B2"].font = font_title
    ws2.row_dimensions[2].height = 34

    ws2.merge_cells("B3:H3")
    ws2["B3"] = "〜 TCP SYN/RSTパケット、OpenTelemetry SDKのフェイルサイレント設計、バッファ破棄の全貌 〜"
    ws2["B3"].font = font_subtitle
    ws2.row_dimensions[3].height = 22

    # Section 1
    ws2.merge_cells("B5:H5")
    ws2["B5"] = "■ 1. 並列起動 vs 直列起動のミリ秒（ms）実行タイムライン"
    ws2["B5"].font = font_section
    ws2["B5"].fill = fill_header_section
    ws2["B5"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws2.row_dimensions[5].height = 26

    headers_tl = [
        "経過時間 (目安)",
        "ECS Agent (ホスト)",
        "ADOTサイドカーの状態",
        "バックエンドの状態",
        "フロントエンドの状態",
        "OSカーネル / ソケット状態\n(127.0.0.1)",
        "並列時のトレース成否"
    ]
    data_tl = [
        [
            "T = 0 ms",
            "タスク起動要求を受信\nコンテナ作成API呼び出し",
            "コンテナ起動開始\n(execve /awscollector)",
            "コンテナ起動開始\n(execve node / java)",
            "コンテナ起動開始\n(execve nginx / node)",
            "ループバックIFのみ存在\nリスナーソケットなし",
            "― (生成前)"
        ],
        [
            "T = 200 ms",
            "Docker start 完了\n(PID作成完了)",
            "Goランタイム初期化\nメモリ確保中...",
            "Node.js/Go ランタイム初期化\nOTel SDK 初期化",
            "Webサーバー起動完了\nポート 80 リッスン開始",
            "ポート 4317 は未割当\nポート 80 が開通",
            "― (準備中)"
        ],
        [
            "T = 500 ms",
            "コンテナ稼働中を検知",
            "設定ファイル読み込み\nYAMLパース、IAMロール解決中",
            "DBコネクションプール確立\n初期化トレース生成！",
            "ALBからヘルスチェック受信\n初期リクエストトレース生成！",
            "バック/フロントが 4317 番に\nTCP SYN パケット送信",
            "× 即座に欠落！\n(TCP RST返却 / Drop)"
        ],
        [
            "T = 1,000 ms",
            "ヘルスチェックポーリング開始",
            "Extensions & Exporters 初期化\nX-Rayクライアント準備中",
            "初期化バッチの送信再試行\nバッファキュー満杯へ",
            "バックエンドAPIを呼び出し\n(しかしバック未開通で502)",
            "4317 未リッスン\n接続拒絶 (ECONNREFUSED)",
            "× 欠落！\n(バッファ溢れで破棄)"
        ],
        [
            "T = 2,500 ms",
            "コンテナ健全性チェック待機",
            "★ bind() & listen() 実行！\nポート 4317 / 4318 開通！",
            "業務APIリクエスト受付可能\n定常運用フェーズへ移行",
            "バック疎通確認成功\n正常ルーティング開始",
            "127.0.0.1:4317 が LISTEN\nTCP 3-way handshake 可能",
            "△ 以降のトレースは成功\n(初期トレースは消失済)"
        ],
        [
            "T = 3,000 ms",
            "ADOTのhealthCheck成功\n(ポート 13133: OK)",
            "定常稼働中 (HEALTHY)\nトレースパイプライン完全稼働",
            "定常稼働中 (HEALTHY)",
            "定常稼働中 (HEALTHY)",
            "全ソケット正常稼働",
            "◎ 完全収集\n(直列なら最初からここ)"
        ]
    ]
    aligns_tl = [align_center, align_left, align_left, align_left, align_left, align_left, align_center]
    widths_tl = [16, 24, 26, 26, 24, 26, 22]
    next_r = format_table(ws2, 6, headers_tl, data_tl, aligns_tl, alt_color=True, col_start=2, col_widths=widths_tl)

    # Section 2
    next_r += 1
    ws2.merge_cells(f"B{next_r}:F{next_r}")
    ws2[f"B{next_r}"] = "■ 2. ネットワーク層・OSカーネル・SDKの動作メカニズム解説"
    ws2[f"B{next_r}"].font = font_section
    ws2[f"B{next_r}"].fill = fill_header_section
    ws2[f"B{next_r}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws2.row_dimensions[next_r].height = 26

    headers_net = [
        "レイヤー / コンポーネント",
        "物理的・プロトコル的挙動",
        "発生するシステムコール / エラー",
        "アプリケーション側の影響",
        "トレースデータの最終的な運命"
    ]
    data_net = [
        [
            "TCP / gRPC\n(OTLP: ポート 4317/4318)",
            "送信元が SYN 送信。受信側ポートが未 listen() のため、OSカーネルが RST (Reset) を即時返却する。",
            "connect() システムコール失敗\nerrno: ECONNREFUSED (接続拒否)",
            "アプリ本体は落とさない（フェイルサイレント）。バックグラウンドでリトライする。",
            "リトライ上限またはバッファ溢れにより、古いスパンから順にメモリ上でサイレント破棄される。"
        ],
        [
            "UDP\n(X-Ray互換: ポート 2000)",
            "コネクションレス通信のため送信元は無条件にパケット送出。カーネルは該当ポートの受信者がいなければ破棄。",
            "ICMP Port Unreachable\n(ただしクライアントは通常無視)",
            "エラーすら発生しない。送信側は正常に送れたと誤認する。",
            "パケットそのものがネットワークスタック内で即座に消滅（完全ロスト）。"
        ],
        [
            "OpenTelemetry SDK\n(BatchSpanProcessor)",
            "ビジネス処理をブロックしないよう、インメモリのリングバッファ（キュー）にスパンを一時保存する。",
            "Queue.offer() / Buffer Overflow",
            "CPU負荷を抑えるため、バッファが満杯（デフォルト2048個等）になると新規スパンを破棄。",
            "起動直後のバーストトラフィックや重い初期化トレースが全てゴミ箱へ直行する。"
        ],
        [
            "ECS Agent\n(awsvpc モード)",
            "タスク内の全コンテナに単一のネットワーク名前空間を共有させ、127.0.0.1 で相互通信させる。",
            "Docker API: ContainerCreate, Start",
            "dependsOn がないと全コンテナを並列起動するため、重いコンテナと軽いコンテナで競争が起きる。",
            "レースコンディションの敗者（初期化の遅いADOT）が、勝者（速いアプリ）の通信を取りこぼす。"
        ]
    ]
    aligns_net = [align_center, align_left, align_left, align_left, align_left]
    widths_net = [22, 34, 30, 32, 36]
    format_table(ws2, next_r + 1, headers_net, data_net, aligns_net, alt_color=True, col_start=2, col_widths=widths_net)

    # Set Column Widths for Sheet 2
    ws2.column_dimensions["A"].width = 3
    ws2.column_dimensions["B"].width = 18
    ws2.column_dimensions["C"].width = 26
    ws2.column_dimensions["D"].width = 28
    ws2.column_dimensions["E"].width = 26
    ws2.column_dimensions["F"].width = 28
    ws2.column_dimensions["G"].width = 28
    ws2.column_dimensions["H"].width = 24

    # =========================================================================
    # SHEET 3: 歴史的背景 & 技術進化年表
    # =========================================================================
    ws3 = wb.create_sheet(title="3_歴史と背景_技術進化年表")
    ws3.views.sheetView[0].showGridLines = True

    ws3.merge_cells("B2:G2")
    ws3["B2"] = "【歴史的背景】分散トレーシングとECSコンテナオーケストレーションの進化史"
    ws3["B2"].font = font_title
    ws3.row_dimensions[2].height = 34

    ws3.merge_cells("B3:G3")
    ws3["B3"] = "〜 なぜ分散トレーシングが必要になり、なぜECSはdependsOnを発明したのか？ 〜"
    ws3["B3"].font = font_subtitle
    ws3.row_dimensions[3].height = 22

    # Section 1
    ws3.merge_cells("B5:G5")
    ws3["B5"] = "■ 分散トレーシングとコンテナオーケストレーションの時代別変遷"
    ws3["B5"].font = font_section
    ws3["B5"].fill = fill_header_section
    ws3["B5"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws3.row_dimensions[5].height = 26

    headers_hist = [
        "年代",
        "時代区分",
        "システム・アーキテクチャの動向",
        "分散トレーシングの進化",
        "AWS ECS / コンテナ機能の進化",
        "当時の現場の課題と解決策"
    ]
    data_hist = [
        [
            "2010年〜\n2013年",
            "モノリス全盛期\nクラウド黎明期",
            "単一の巨大アプリケーション (Rails, Java EE)。1台のEC2上でDBと共に稼働。",
            "Googleが「Dapper」論文を発表。分散トレーシングの概念が世界に提示される。",
            "Docker未登場。仮想マシン (EC2) や物理サーバーが中心。",
            "ログはローカルファイル (/var/log) に保存。SSHで入って grep すれば調査完了。"
        ],
        [
            "2014年〜\n2016年",
            "マイクロサービス\nコンテナ革命",
            "サービス分割が進み、リクエストがネットワークを越えて数十台を飛び交うように変化。",
            "TwitterがZipkinをOSS化。UberがJaegerを開発。トレース追跡が現実化。",
            "2015年に AWS ECS がローンチ！タスク定義による複数コンテナ定義が登場。",
            "リクエストがどこで遅延・失敗したか追跡不能に。分散トレースツールの導入競争が激化。"
        ],
        [
            "2017年〜\n2018年",
            "規格分断期と\nECS初期の苦悩",
            "サイドカーパターンが普及。アプリの横にログ/トレース収集エージェントを配置。",
            "OpenTracing（CNCF）と OpenCensus（Google）に二分され、開発現場が大混乱。",
            "ECSにはコンテナ起動順序を制御する機能が一切存在しなかった！",
            "【wait-for-it地獄】ENTRYPOINTでシェルスクリプトを回し、nc や curl で待機する泥臭いハックが横行。"
        ],
        [
            "2019年末",
            "★ 大転換点\n(dependsOn登場)",
            "クラウドネイティブの成熟。KubernetesとECSのエンタープライズ採用が標準化。",
            "二大派閥が電撃合併し「OpenTelemetry (OTel)」プロジェクトがCNCFで発足！",
            "★ AWS ECSが「コンテナ依存関係 (dependsOn)」を正式リリース！！",
            "シェルスクリプト待機が全廃。タスク定義で START / HEALTHY を宣言的に制御可能に！"
        ],
        [
            "2020年〜\n2022年",
            "OTel標準化と\nADOTの台頭",
            "AWSもオープンソース標準への追随を決定。独自プロトコルからOTelへの移行。",
            "AWSが「AWS Distro for OpenTelemetry (ADOT)」を正式発表・GAリリース。",
            "旧X-Rayデーモンから ADOT Collector サイドカーへの移行が推奨される。",
            "ADOTの起動時間（Go製で2秒程度）に伴い、dependsOn を使わないと初期トレースが抜ける問題が顕在化。"
        ],
        [
            "2023年〜\n2026年最新",
            "ゼロロス観測と\n高信頼インフラ",
            "コールドスタート極小化、サーバレスコンテナ (Fargate) での厳密な可観測性。",
            "OpenTelemetryが業界標準として完全定着。Traces/Metrics/Logs の三位一体化。",
            "ECS Exec、ECS Service Connect、ヘルスチェック連携の成熟。",
            "【現代の結論】ADOTのhealthCheck (13133) + dependsOn (HEALTHY) + startPeriod が鉄則パターンとして確立。"
        ]
    ]
    aligns_hist = [align_center, align_center, align_left, align_left, align_left, align_left]
    widths_hist = [14, 18, 30, 30, 30, 42]
    format_table(ws3, 6, headers_hist, data_hist, aligns_hist, alt_color=True, col_start=2, col_widths=widths_hist)

    # Set Column Widths for Sheet 3
    ws3.column_dimensions["A"].width = 3
    ws3.column_dimensions["B"].width = 16
    ws3.column_dimensions["C"].width = 20
    ws3.column_dimensions["D"].width = 32
    ws3.column_dimensions["E"].width = 32
    ws3.column_dimensions["F"].width = 32
    ws3.column_dimensions["G"].width = 44

    # =========================================================================
    # SHEET 4: ECS設定リファレンス & パラメータ
    # =========================================================================
    ws4 = wb.create_sheet(title="4_ECS設定リファレンス")
    ws4.views.sheetView[0].showGridLines = True

    ws4.merge_cells("B2:F2")
    ws4["B2"] = "【ECSタスク定義】dependsOn・healthCheck・startPeriod 設計仕様"
    ws4["B2"].font = font_title
    ws4.row_dimensions[2].height = 34

    ws4.merge_cells("B3:F3")
    ws4["B3"] = "〜 トレース欠落を確実にゼロにするためのパラメータ設定とアンチパターン回避策 〜"
    ws4["B3"].font = font_subtitle
    ws4.row_dimensions[3].height = 22

    # Section 1
    ws4.merge_cells("B5:F5")
    ws4["B5"] = "■ 1. dependsOn の4つの条件（condition）の比較とトレース観測での評価"
    ws4["B5"].font = font_section
    ws4["B5"].fill = fill_header_section
    ws4["B5"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws4.row_dimensions[5].height = 26

    headers_cond = [
        "条件名 (condition)",
        "ECS Agentによる到達判定タイミング",
        "ADOTサイドカーでの適用",
        "判定の理由と現場での落とし穴",
        "推奨度"
    ]
    data_cond = [
        [
            "START",
            "Docker Engineがプロセス (PID) を生成した瞬間 (execve 完了直後)",
            "× 非推奨 (欠落する)",
            "【最大の罠】プロセスは動いていても、ADOT内部の設定ロードやポート 4317 のリッスンは完了していないため、初期トレースが全て欠落する。",
            "× 危険"
        ],
        [
            "HEALTHY",
            "コンテナ内の healthCheck コマンドが exit 0 (成功) を返した瞬間",
            "◎ 必須 (完全保証)",
            "ADOTが受信ソケット (4317/4318) を開き、受信準備が100%整ったことを確認してからアプリを動かせるため、欠落が完全に防げる。",
            "◎ 推奨 (必須)"
        ],
        [
            "COMPLETE",
            "コンテナプロセスが終了した瞬間 (終了コードは問わない)",
            "× 不可",
            "ADOTは常駐型サイドカープロセスであるため、終了することはない。指定すると後続コンテナが永遠に起動しない。",
            "× 使用不可"
        ],
        [
            "SUCCESS",
            "コンテナプロセスがステータスコード 0 で正常終了した瞬間",
            "× 不可",
            "DBマイグレーションや初期化スクリプトなど、一度だけ実行して終了する init コンテナ専用の条件。",
            "× 使用不可"
        ]
    ]
    aligns_cond = [align_center, align_left, align_center, align_left, align_center]
    widths_cond = [18, 32, 22, 44, 16]
    next_r = format_table(ws4, 6, headers_cond, data_cond, aligns_cond, alt_color=True, col_start=2, col_widths=widths_cond)

    # Section 2
    next_r += 1
    ws4.merge_cells(f"B{next_r}:F{next_r}")
    ws4[f"B{next_r}"] = "■ 2. healthCheck および startPeriod パラメータ設計リファレンス"
    ws4[f"B{next_r}"].font = font_section
    ws4[f"B{next_r}"].fill = fill_header_section
    ws4[f"B{next_r}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws4.row_dimensions[next_r].height = 26

    headers_hc = [
        "パラメータ名",
        "対象コンテナ",
        "本番推奨値",
        "役割と技術的根拠",
        "不適切に設定した場合の障害リスク"
    ]
    data_hc = [
        [
            "command",
            "adot-collector",
            "[\"CMD-SHELL\", \"curl -f http://localhost:13133/ || exit 1\"]",
            "ADOTの health_check エクステンション（ポート 13133）を叩いてパイプラインの準備状態を検証。",
            "存在しないポートを指定すると永久に UNHEALTHY となり、タスク全体が起動失敗する。"
        ],
        [
            "startPeriod",
            "adot-collector",
            "10 (秒)",
            "コンテナ起動直後の初期化猶予期間。この期間内のヘルスチェック失敗はリトライ回数にカウントされない。",
            "設定しない（0秒）場合、起動直後の1〜2秒の準備中にヘルスチェックが走り、即座に異常判定される。"
        ],
        [
            "interval",
            "adot-collector",
            "5 (秒)",
            "ヘルスチェックのポーリング間隔。短すぎると負荷になり、長すぎると後続起動が遅れる。",
            "30秒などにすると、ADOTの準備が完了していても後続のバックエンド起動まで最長30秒待たされる。"
        ],
        [
            "timeout",
            "adot-collector",
            "2 (秒)",
            "ヘルスチェックコマンドの応答タイムアウト時間。",
            "短すぎるとCPUバースト時に誤ってタイムアウト失敗と判定される。"
        ],
        [
            "retries",
            "adot-collector",
            "3 (回)",
            "ヘルスチェックが連続失敗した際に UNHEALTHY とみなす上限回数。",
            "1回にするとネットワークの一時的な揺らぎでコンテナが強制停止される。"
        ],
        [
            "startPeriod",
            "backend (Java/Spring)",
            "30 〜 60 (秒)",
            "JVMやSpringフレームワーク、DB初期プールのウォームアップ時間を吸収するための猶予期間。",
            "短いと初回起動の重さでヘルスチェックが落ち、ECSがタスクを再起動ループに追い込む。"
        ]
    ]
    aligns_hc = [align_center, align_center, align_left, align_left, align_left]
    widths_hc = [18, 24, 32, 42, 38]
    format_table(ws4, next_r + 1, headers_hc, data_hc, aligns_hc, alt_color=True, col_start=2, col_widths=widths_hc)

    # Set Column Widths for Sheet 4
    ws4.column_dimensions["A"].width = 3
    ws4.column_dimensions["B"].width = 18
    ws4.column_dimensions["C"].width = 24
    ws4.column_dimensions["D"].width = 34
    ws4.column_dimensions["E"].width = 44
    ws4.column_dimensions["F"].width = 40

    # =========================================================================
    # SHEET 5: 小学生向けストーリー解説
    # =========================================================================
    ws5 = wb.create_sheet(title="5_小学生向けストーリー解説")
    ws5.views.sheetView[0].showGridLines = True

    ws5.merge_cells("B2:E2")
    ws5["B2"] = "【小学生向け物語】まぼろしの学芸会ビデオ事件"
    ws5["B2"].font = font_title
    ws5.row_dimensions[2].height = 34

    ws5.merge_cells("B3:E3")
    ws5["B3"] = "〜 なぜADOTくんは最初を撮れなかったのか？ 順序（dependsOn）の大切さを学ぼう 〜"
    ws5["B3"].font = font_subtitle
    ws5.row_dimensions[3].height = 22

    # Section 1
    ws5.merge_cells("B5:E5")
    ws5["B5"] = "■ 登場人物のプロフィール"
    ws5["B5"].font = font_section
    ws5["B5"].fill = fill_header_section
    ws5["B5"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws5.row_dimensions[5].height = 26

    headers_char = [
        "キャラクター",
        "コンピューターの世界での名前",
        "学芸会でのしごと",
        "とくちょう・性格"
    ]
    data_char = [
        [
            "ADOT（エードット）くん",
            "ADOT サイドカーコンテナ\n(aws-otel-collector)",
            "ビデオカメラ係（記録係）。劇の様子を全部録画して校長先生（CloudWatch）に届ける。",
            "とても真面目で絶対にウソをつかない。でも三脚を立ててピントを合わせるのに少し時間がかかる。"
        ],
        [
            "バックエンドくん",
            "バックエンドコンテナ\n(API・ビジネスロジック)",
            "舞台裏の音響・大道具係。劇の音楽（BGM）を鳴らしたり、ライトをつけたりする裏方。",
            "力持ちで頼りになる。アンプの電源を入れて音を合わせる準備が必要。"
        ],
        [
            "フロントエンドくん",
            "フロントエンドコンテナ\n(Web UI / Nginx)",
            "ステージの司会者・主役。お客さん（ユーザー）を笑顔で迎えてお話しする。",
            "足がとても速くてせっかち。幕が開いたらすぐにしゃべり始める。"
        ],
        [
            "ECS（イーシーエス）先生",
            "Amazon ECS Agent\n(オーケストレーター)",
            "学芸会を取り仕切る担任の先生。みんなに「始めて！」と合図を出す。",
            "ルールが決められていないと「みんな一斉によーいドン！」と言ってしまう癖がある。"
        ]
    ]
    aligns_char = [align_center, align_center, align_left, align_left]
    widths_char = [20, 26, 36, 42]
    next_r = format_table(ws5, 6, headers_char, data_char, aligns_char, alt_color=True, col_start=2, col_widths=widths_char)

    # Section 2
    next_r += 1
    ws5.merge_cells(f"B{next_r}:E{next_r}")
    ws5[f"B{next_r}"] = "■ 物語：どうしてビデオが消えてしまったの？"
    ws5[f"B{next_r}"].font = font_section
    ws5[f"B{next_r}"].fill = fill_header_section
    ws5[f"B{next_r}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws5.row_dimensions[next_r].height = 26

    headers_story = [
        "場面（シーン）",
        "できごと",
        "そのとき何が起きていたの？（ITの解説）",
        "教訓・ポイント"
    ]
    data_story = [
        [
            "第1話：\n「よーいドン！」の大混乱",
            "ECS先生が「時間です！全員一斉に準備して！」と叫びました。\n足の速い司会者（フロント）は、すぐに幕を開けて「こんにちは！」とお客さんを迎えました。",
            "これが【並列起動】です。コンテナが一斉に立ち上がりますが、アプリは一瞬で動き始めます。",
            "みんなが同じスピードで準備できるとは限りません。"
        ],
        [
            "第2話：\n消えた合図と届かない音",
            "司会者は「いまお客さんが来たよ！」とADOTくんに手を振りましたが、ADOTくんはまだ三脚を広げている最中！\nさらに「BGM流して！」と頼まれた音響係もまだアンプを温めていて、音が出ませんでした。",
            "ADOTはまだポートを開いていないため、トレースデータは拒絶 (RST) されてゴミ箱へ。\nバックエンドも未準備のため 502 Bad Gateway が発生しました。",
            "受け取る相手の準備ができていないのにボールを投げても、誰もキャッチできません。"
        ],
        [
            "第3話：\n校長先生のお怒り",
            "劇が終わった後、校長先生が「最初の挨拶のとき、どうして音楽が鳴らなかったんだ？ビデオを見せてくれ！」と言いました。\nでもADOTくんのカメラには、途中からの映像しか残っていませんでした。",
            "トラブルの原因（コールドスタート時のエラー）を調査しようとしても、X-Rayにトレースが一切残っておらず原因究明が不可能になりました。",
            "一番大切な「最初のトラブルの瞬間」ほど、記録に残りにくいのです。"
        ],
        [
            "第4話：\n作戦変更！「合図のリレー」",
            "そこで先生は新しいルールを決めました。\n① まずADOTくんがカメラを構えて「録画OK！」の赤いランプをつける (HEALTHY)\n② それを見て音響係が準備を整える (HEALTHY)\n③ 最後に司会者が幕を開ける！",
            "これが【直列起動（dependsOn）】です！\n前段のコンテナがヘルスチェックに合格するまで、後段のコンテナは絶対に起動しません。",
            "順番を守るだけで、すべての問題が一気に解決します！"
        ],
        [
            "最終話：\n大成功の学芸会",
            "順番を守ったことで、音響のBGMの1音目から、司会者の一言目、お客さんの拍手まで、\n最初から最後まで1秒も欠けることなく、綺麗なビデオが校長先生に届けられました！",
            "タスクが立ち上がった瞬間の初期化トレースから、本番リクエストまで、100%完全な分散トレーシングが実現しました。",
            "【結論】ADOTは必ず HEALTHY を待ってからアプリを動かそう！"
        ]
    ]
    aligns_story = [align_center, align_left, align_left, align_left]
    widths_story = [18, 38, 42, 42]
    format_table(ws5, next_r + 1, headers_story, data_story, aligns_story, alt_color=True, col_start=2, col_widths=widths_story)

    # Set Column Widths for Sheet 5
    ws5.column_dimensions["A"].width = 3
    ws5.column_dimensions["B"].width = 18
    ws5.column_dimensions["C"].width = 38
    ws5.column_dimensions["D"].width = 42
    ws5.column_dimensions["E"].width = 44

    # Remove default sheet
    wb.remove(default_sheet)

    # Save workbook
    output_filename = "ECS_ADOT_Startup_Order_Guide.xlsx"
    wb.save(output_filename)
    print(f"Successfully generated {output_filename}")

if __name__ == "__main__":
    build_excel()
