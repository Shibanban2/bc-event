let data = {};
const now = new Date();

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

function parseDates(text) {
  const match = text.match(
    /(\d{2})\/(\d{2})(?:\((\d{1,2}):(\d{2})\))?[^0-9]*(\d{2})\/(\d{2})(?:\((\d{1,2}):(\d{2})\))?|(\d{2})\/(\d{2})(?:\((\d{1,2}):(\d{2})\))?/
  );

  const now = new Date();
  const thisYear = now.getFullYear();
  let start = null;
  let end = null;

  if (match) {
    if (match[1]) {
      // 開始日
      let startMonth = parseInt(match[1]);
      let startDay = parseInt(match[2]);
      let startHour = match[3] ? parseInt(match[3]) : 11; // デフォルト 11:00
      let startMinute = match[4] ? parseInt(match[4]) : 0;
      let startYear = thisYear;

      if (now.getMonth() + 1 === 12 && startMonth < 12) {
        startYear++;
      }
      start = new Date(startYear, startMonth - 1, startDay, startHour, startMinute, 0, 0);

      // 終了日
      let endMonth = parseInt(match[5]);
      let endDay = parseInt(match[6]);
      let endHour = match[7] ? parseInt(match[7]) : 11;
      let endMinute = match[8] ? parseInt(match[8]) : 0;
      let endYear = thisYear;

      if (now.getMonth() + 1 === 12 && endMonth < 12) {
        endYear++;
      }
      end = new Date(endYear, endMonth - 1, endDay, endHour, endMinute, 0, 0);
    } else if (match[9]) {
      // 単発日 (終了日なし)
      let startMonth = parseInt(match[9]);
      let startDay = parseInt(match[10]);
      let startHour = match[11] ? parseInt(match[11]) : 11;
      let startMinute = match[12] ? parseInt(match[12]) : 0;
      let startYear = thisYear;

      if (now.getMonth() + 1 === 12 && startMonth < 12) {
        startYear++;
      }
      start = new Date(startYear, startMonth - 1, startDay, startHour, startMinute, 0, 0);
    }
  }
  return { start, end };
}


function isPermanent(text) {
  return /常設|#常設/i.test(text);
}

function renderContent(id, showCurrent) {
  const container = document.getElementById(id);
  container.innerHTML = '';

  const order = ['gatya', 'sale', 'item', 'mission'];
  const sections = id === 'all' ? order : [id];

  for (const key of sections) {
    const title = document.createElement('div');
    title.className = 'section-title';
    title.textContent = key;
    container.appendChild(title);

    let entries = data[key] || [];

    if (document.getElementById('sortByDate').checked) {
      entries = [...entries].sort((a, b) => {
        const textA = typeof a === 'string' ? a : a.title;
        const textB = typeof b === 'string' ? b : b.title;
        const { start: startA } = parseDates(textA);
        const { start: startB } = parseDates(textB);
        if (!startA && !startB) return 0;
        if (!startA) return 1;
        if (!startB) return -1;
        return startA - startB;
      });
    }

    let count = 0;

    for (let i = 0; i < entries.length; i++) {
      const item = entries[i];
      const text = typeof item === 'string' ? item : item.title;
      const detail = typeof item === 'string' ? '' : item.detail;

      if (key === 'gatya' && (/プラチナガチャ|レジェンドガチャ/.test(text))) continue;
      if (key === 'item' && (/道場報酬|報酬設定|ログボ:35030|ログボ:35031|ログボ:35032|ログボ:981/.test(text))) continue;
      if (key === 'sale' && (/絶・誘惑のシンフォニー|地図グループ16|ジャンボーグ鈴木大降臨|地図グループ17|地図グループ18|ケン 第3形態進化権/.test(text))) continue;
      if (key === 'mission' && (/にゃんチケドロップステージを3回クリアしよう|XPドロップステージを5回クリアしよう|レジェンドストーリーを5回クリアしよう|ガマトトを探検に出発させて7回探検終了させよう|ガマトトを探検に出発させて10回探検終了させよう|レジェンドストーリーを10回クリアしよう|対象ステージは「にゃんこミッションとは？」をご確認下さい|マタタビドロップステージを3回クリアしよう|おかえりミッション/.test(text))) continue;

      const { start, end } = parseDates(text);
      const permanent = isPermanent(text);

      let shouldShow = false;
      if (showCurrent) {
        shouldShow = permanent || (start && now >= start && (!end || now < end)) || (start && now < start);
      } else {
        shouldShow = permanent || (start && now < start);
      }

      if (!shouldShow) continue;

      const div = document.createElement('div');
      div.className = 'event-card';

      if (!/ミッション/.test(text)) {
        if (/確定|闇目|ガチャ半額リセット/.test(text)) {
          div.classList.add('red');
        } else if (/強襲|ランキングの間|異次元コロシアム/.test(text)) {
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
      none.textContent = '現在、予定されているイベントはありません。';
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

document.getElementById('sortByDate').addEventListener('change', () => {
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
