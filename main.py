PREFIX = "s."  # モジュールのトップレベルで定義

@client.event
async def on_ready():
    print(f"ログインしました: {client.user.name}")

async def fetch_tsv(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                print(f"Fetching {url}: Status {resp.status}")  # デバッグログ
                if resp.status != 200:
                    print(f"Failed to fetch {url}: Status {resp.status}")
                    return []
                text = await resp.text()
                print(f"TSV content: {text[:100]}...")  # 最初の100文字を表示
                lines = text.splitlines()
                rows = []
                for line in lines:
                    row = line.split("\t")
                    if "".join(row).strip() == "":
                        continue
                    while len(row) > 0 and row[-1] == "":
                        row.pop()
                    if len(row) == 0 or (row[-1] not in ("0", "1")):
                        row = row + ["0"]
                    rows.append(row)
                print(f"Parsed {len(rows)} rows from {url}")  # デバッグログ
                return rows
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

async def load_stage_map():
    url = "https://shibanban2.github.io/bc-event/token/stage.tsv"
    rows = await fetch_tsv(url)
    stage_map = {}
    for row in rows:
        if len(row) >= 2:
            try:
                sid = int(row[0])
                name = row[1]
                stage_map[sid] = name
            except ValueError:
                continue
    print(f"Loaded stage_map: {stage_map}")  # デバッグログ
    return stage_map

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.lower() == "ping.":
        await message.channel.send("Pong.")

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
        except Exception as e:
            print(f"Error in {PREFIX}sale command: {e}")
            await message.channel.send("エラーが発生しました。管理者に連絡してください。")

    if message.content.lower().startswith(f"{PREFIX}gt"):
        try:
            gatya_rows, name_map, item_map = await load_gatya_maps()
            outputs = []
            for row in gatya_rows[1:]:
                lines = parse_gatya_row(row, name_map, item_map)
                outputs.extend(lines)
            
            if outputs:
                await message.channel.send("\n".join(outputs))
            else:
                await message.channel.send("ガチャ情報は見つかりませんでした")
        except Exception as e:
            print(f"Error in {PREFIX}gt command: {e}")
            await message.channel.send("エラーが発生しました。管理者に連絡してください。")

# 実行
keep_alive()
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN:
    client.run(TOKEN)
else:
    print("Tokenが見つかりませんでした")