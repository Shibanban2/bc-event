def format_time(t):
    try:
        t = int(t)
        hour = str(t // 100).zfill(2)
        min = str(t % 100).zfill(2)
        return f"{hour}:{min}"
    except (ValueError, TypeError):
        return "00:00"

def parse_gatya_row(row, name_map, item_map, today_str="20250823"):
    output_lines = []
    try:
        start_date = str(row[0])
        start_time = row[1]
        end_date = str(row[2])
        end_time = row[3]
        type_code = int(row[8]) if len(row) > 8 and row[8].isdigit() else 0
        j = int(row[9]) if len(row) > 9 and row[9].isdigit() else 0
        print(f"Processing row: {row[:10]}")
    except (IndexError, ValueError, TypeError) as e:
        print(f"Invalid row format: {row}, error: {e}")
        return output_lines

    # 終了日が今日以降、かつ 20300101 でない場合に表示
    if end_date < today_str or end_date == "20300101":
        return output_lines

    base_cols = {
        1: {"id": 10, "extra": 13, "normal": 14, "rare": 16, "super": 18, "ultra": 20, "confirm": 21, "legend": 22, "title": 24},
        2: {"id": 25, "extra": 28, "normal": 29, "rare": 31, "super": 33, "ultra": 35, "confirm": 36, "legend": 37, "title": 39},
        3: {"id": 40, "extra": 43, "normal": 44, "rare": 46, "super": 48, "ultra": 50, "confirm": 51, "legend": 52, "title": 54},
        4: {"id": 55, "extra": 58, "normal": 59, "rare": 61, "super": 63, "ultra": 65, "confirm": 66, "legend": 67, "title": 69},
        5: {"id": 70, "extra": 73, "normal": 74, "rare": 76, "super": 78, "ultra": 80, "confirm": 81, "legend": 82, "title": 84},
        6: {"id": 85, "extra": 88, "normal": 89, "rare": 91, "super": 93, "ultra": 95, "confirm": 96, "legend": 97, "title": 99},
        7: {"id": 100, "extra": 103, "normal": 104, "rare": 106, "super": 108, "ultra": 110, "confirm": 111, "legend": 112, "title": 114},
    }

    # 特例: typeCode=4 かつ j=2
    if type_code == 4 and j == 2:
        try:
            id = int(row[27]) if len(row) > 27 and row[27].isdigit() else -1
            extra = lookup_extra(row[28], item_map) if len(row) > 28 else ""
            title = "".join([row[i] for i in range(40, 43) if len(row) > i and row[i]]) if len(row) > 42 else ""
        except (IndexError, ValueError, TypeError) as e:
            print(f"Error in special case (type=4, j=2): {e}")
            return output_lines
        if id <= 0:
            return output_lines
        gname = name_map.get(id, f"error[{id}]")
        date_range = f"{format_date(start_date)}({get_day_of_week(start_date)}) {format_time(start_time)}〜{format_date(end_date)}({get_day_of_week(end_date)}) {format_time(end_time)}"
        col_k = f"{date_range}\n　{id} {gname}"
        if extra:
            col_k += f" {extra}"
        output_lines.append(col_k)
        return output_lines

    # 通常処理
    col = base_cols.get(j)
    if not col:
        print(f"Invalid j value: {j}")
        return output_lines

    try:
        id = int(row[col["id"]]) if len(row) > col["id"] and row[col["id"]].isdigit() else -1
        extra = lookup_extra(row[col["extra"]], item_map) if len(row) > col["extra"] else ""
        confirm = "【確定】" if len(row) > col["confirm"] and row[col["confirm"]] == "1" and type_code != 4 else ""
        title = row[col["title"]] if len(row) > col["title"] and row[col["title"]] else ""
    except (IndexError, ValueError, TypeError) as e:
        print(f"Error processing row at col {col}: {e}")
        return output_lines

    if id <= 0:
        return output_lines

    gname = name_map.get(id, f"error[{id}]")
    date_range = f"{format_date(start_date)}({get_day_of_week(start_date)}) {format_time(start_time)}〜{format_date(end_date)}({get_day_of_week(end_date)}) {format_time(end_time)}"
    col_k = f"{date_range}\n　{id} {gname}{confirm}"
    if extra:
        col_k += f" {extra}"
    output_lines.append(col_k)
    return output_lines

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.lower() == "s.ping":
        await message.channel.send("Pong.")
    if message.content.lower() == f"{PREFIX}help":
        await message.channel.send(
            "s.sale [ID or 名前]: ステージの販売スケジュールを表示。例: s.sale 50 や s.sale ガチャ\n"
            "s.gt: 今日以降のガチャスケジュールを表示（終了日基準、永続は除く）。"
        )
    if message.content.lower().startswith(f"{PREFIX}sale "):
        try:
            query = message.content.split(" ", 1)[1].strip()
            sale_id = None
            sale_name = None
            try:
                sale_id = int(query)
            except ValueError:
                sale_name = query
            sale_url = "https://shibanban2.github.io/bc-event/token/sale.tsv"
            rows = await fetch_tsv(sale_url)
            stage_map = await load_stage_map()
            outputs = []
            found_ids = set()
            header = None
            if sale_id is not None:
                stage_name = stage_map.get(sale_id, "")
                header = f"[{sale_id} {stage_name}]"
            elif sale_name is not None:
                header = f"[??? {sale_name}]"
            for row in rows:
                ids = extract_event_ids(row)
                for eid in ids:
                    name = stage_map.get(eid, "")
                    if sale_id is not None and eid != sale_id:
                        continue
                    if sale_name is not None and sale_name not in name:
                        continue
                    header = f"[{eid} {name}]" if name else f"[{eid}]"
                    if eid not in found_ids:
                        outputs.append(header)
                        found_ids.add(eid)
                    note = build_monthly_note(row)
                    period_line = _fmt_date_range_line(row)
                    ver_line = _version_line(row)
                    if note:
                        outputs.append(f"{period_line}\n{ver_line}\n```{note}```")
                    else:
                        outputs.append(f"{period_line}\n{ver_line}")
            if outputs:
                await message.channel.send("\n".join(outputs))
            else:
                if header is None:
                    header = "[]"
                await message.channel.send(f"{header}\nスケジュールが見つかりませんでした")
        except Exception as e:
            print(f"Error in {PREFIX}sale command: {e}")
            await message.channel.send("エラーが発生しました。")
    if message.content.lower().startswith(f"{PREFIX}gt"):
        try:
            gatya_rows, name_map, item_map = await load_gatya_maps()
            outputs = []
            today_str = datetime.now().strftime("%Y%m%d")  # 今日の日付（例：20250823）
            for row in gatya_rows[1:]:  # ヘッダー行をスキップ
                lines = parse_gatya_row(row, name_map, item_map, today_str)
                outputs.extend(lines)
            if outputs:
                await message.channel.send("\n".join(outputs))
            else:
                await message.channel.send("今日以降のガチャ情報は見つかりませんでした")
        except Exception as e:
            print(f"Error in {PREFIX}gt command: {e}")
            await message.channel.send("エラーが発生しました。")