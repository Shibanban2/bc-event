@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() == "ping.":
        await message.channel.send("Pong.")

    if message.content.startswith(f"{PREFIX}sale "):
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

        # sale_id が指定された場合、stage_map から名前を取得
        header = None
        if sale_id is not None:
            stage_name = stage_map.get(sale_id, "不明なステージ")
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
                header = "[不明]"
            await message.channel.send(f"{header}\n該当するスケジュールは見つかりませんでした")