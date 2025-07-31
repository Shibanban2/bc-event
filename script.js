// script.js
let data = {};

const now = new Date();
now.setHours(11, 0, 0, 0);

fetch('https://Shibanban2.github.io/bc-event/data.json')
  .then(res => res.json())
  .then(json => {
    data = json;
    preprocessData();
    renderContent('gatya', false);
  });

function preprocessData() {
  if (data.item) {
    const moved = data.item.filter(e => e.title && /ガチャ半額リセット/.test(e.title));
    if (moved.length > 0) {
      data.item = data.item.filter(e => !/ガチャ半額リセット/.test(e.title));
      data.gatya = [...moved, ...(data.gatya || [])];
    }
  }
}

function parseDateRange(text) {
  const match = text.match(/(\d{2})\/(\d{2})[〜~\-―](\d{2})\/(\d{2})/);
  if (!match) return { start: null, end: null };

  const year = now.getFullYear();
  const start = new Date(year, parseInt(match[1]) - 1, parseInt(match[2]));
  const end = new Date(year, parseInt(match[3]) - 1, parseInt(match[4]));

  start.setHours(11, 0, 0, 0);
  end.setHours(11, 0, 0, 0);

  return { start, end };
}

function renderContent(id, showAll) {
  const container = document.getElementById(id);
  container.innerHTML = '';

  const order = ['gatya', 'sale', 'item', 'mission'];
  const sections = id === 'all' ? order : [id];

  const today = new Date();
  today.setHours(11, 0, 0, 0);

  for (const key of sections) {
    const title = document.createElement('div');
    title.className = 'section-title';
    title.textContent = key;
    container.appendChild(title);

    const entries = data[key] || [];
    let count = 0;

    for (const entry of entries) {
      const text = typeof entry === 'string' ? entry : entry.title;
      const detail = typeof entry === 'string' ? '' : entry.detail;

      // 除外条件（ここは元のまま、省略）
      if (key === 'gatya' && (/プラチナガチャ|レジェンドガチャ/.test(text))) continue;
      if (key === 'item' && (/道場報酬|報酬設定|ログボ:35030|ログボ:35031| ログボ:35032|ログボ:981/.test(text))) continue;
      if (key === 'sale' && (/進化の緑マタタビ|進化の紫マタタビ|進化の赤マタタビ|進化の青マタタビ|進化の黄マタタビ|絶・誘惑のシンフォニー|地図グループ16|地図グループ17|地図グループ18/.test(text))) continue;
      if (key === 'mission' && (/にゃんチケドロップステージを3回クリアしよう|XPドロップステージを5回クリアしよう|レジェンドストーリーを5回クリアしよう|ガマトトを探検に出発させて7回探検終了させよう|ウィークリーミッションをすべてクリアしよう|ガマトトを探検に出発させて10回探検終了させよう|レジェンドストーリーを10回クリアしよう|対象ステージは「にゃんこミッションとは？」をご確認下さい|マタタビドロップステージを3回クリアしよう|おかえりミッション/.test(text))) continue;

    const { start, end } = parseDateRange(text);
      const isPermanent = /常設|#常設/.test(text);

      let show = false;

      if (showAll) {
        show = (start && end && today >= start && today <= end)
             || (start && today < start)
             || isPermanent;
      } else {
        show = (start && today < start)
             || isPermanent;
      }

      if (!show) continue;

      const div = document.createElement('div');
      div.className = 'event-card';

      if (!/ミッション/.test(text)) {
        if (/祭|確定|レジェンドクエスト|風雲にゃんこ塔|異界にゃんこ塔|グランドアビス|闇目|ねこの目洞窟|ガチャ半額リセット|確率2倍|にゃんこスロット|必要/.test(text)) {
          div.classList.add('red');
        } else if (/おまけアップ|異次元コロシアム|強襲|ランキングの間|ネコ基地トーク/.test(text)) {
          div.classList.add('blue');
        }
      }

      div.innerHTML = text;

      if (detail) {
        div.addEventListener('click', () => openModal(detail));
      }

      container.appendChild(div);
      count++;
    }

    if (count === 0) {
      const none = document.createElement('div');
      none.textContent = '表示できるイベントはありません';
      container.appendChild(none);
    }
  }
}

function showTab(id) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.content').forEach(c => c.classList.add('hidden'));

  document.querySelector(`.tab[onclick="showTab('${id}')"]`).classList.add('active');
  document.getElementById(id).classList.remove('hidden');

  renderContent(id, document.getElementById('showAll').checked);
}

document.getElementById('showAll').addEventListener('change', () => {
  const activeTab = document.querySelector('.tab.active').textContent.trim();
  const id = activeTab === 'すべての予定' ? 'all' : activeTab;
  renderContent(id, document.getElementById('showAll').checked);
});

function openModal(content) {
  document.getElementById('modal-body').innerHTML = content;
  document.getElementById('detail-modal').classList.add('show');
}

function closeModal() {
  document.getElementById('detail-modal').classList.remove('show');
}

document.getElementById('modal-close').addEventListener('click', closeModal);
document.getElementById('detail-modal').addEventListener('click', e => {
  if (e.target.id === 'detail-modal') closeModal();
});

document.getElementById('save-btn').addEventListener('click', () => {
  const today = new Date();
  const yyyy = today.getFullYear();
  const mm = String(today.getMonth() + 1).padStart(2, '0');
  const dd = String(today.getDate()).padStart(2, '0');
  const fileName = `nyanko_schedule_${yyyy}-${mm}-${dd}.png`;

  html2canvas(document.body, {
    backgroundColor: '#ffffff',
    useCORS: true
  }).then(canvas => {
    const link = document.createElement('a');
    link.download = fileName;
    link.href = canvas.toDataURL('image/png');
    link.click();
  });
});
