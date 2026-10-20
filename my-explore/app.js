let galleryData = [];

// 상위 카테고리별 에피소드 범위 매핑
const categoryEpMap = {
  'Ⅰ. 한국인을 이해하기': Array.from({length: 20}, (_, i) => `EP.${String(i + 1).padStart(2, '0')}`),
  'Ⅱ. 음식과 식생활': Array.from({length: 15}, (_, i) => `EP.${String(i + 21).padStart(2, '0')}`),
  'Ⅲ. 예절·인간관계': Array.from({length: 15}, (_, i) => `EP.${String(i + 36).padStart(2, '0')}`),
  'Ⅳ. 한국인의 일상': Array.from({length: 15}, (_, i) => `EP.${String(i + 51).padStart(2, '0')}`),
  'Ⅴ. 학교·청소년': Array.from({length: 10}, (_, i) => `EP.${String(i + 66).padStart(2, '0')}`),
  'Ⅵ. 한국의 역사': Array.from({length: 10}, (_, i) => `EP.${String(i + 76).padStart(2, '0')}`),
  'Ⅶ. 교통·기술·도시': Array.from({length: 8}, (_, i) => `EP.${String(i + 86).padStart(2, '0')}`),
  'Ⅷ. 여행·지리·감성': Array.from({length: 7}, (_, i) => `EP.${String(i + 94).padStart(2, '0')}`)
};

// 기본 gallery.csv 자동 불러오기
window.addEventListener('DOMContentLoaded', () => {
  fetch('gallery.csv')
    .then(res => res.text())
    .then(csvText => {
      parseCSV(csvText);
    })
    .catch(() => {
      console.warn("gallery.csv 불러오기 실패.");
    });
});

// CSV 파싱 엔진 (줄바꿈이 포함된 큰따옴표 필드 처리 지원)
function parseCSV(text) {
  const lines = [];
  let field = '';
  let inQuotes = false;
  let currentLine = [];

  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    const nextChar = text[i + 1];

    if (char === '"') {
      if (inQuotes && nextChar === '"') {
        field += '"';
        i++;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (char === ',' && !inQuotes) {
      currentLine.push(field.trim());
      field = '';
    } else if ((char === '\r' || char === '\n') && !inQuotes) {
      if (char === '\r' && nextChar === '\n') {
        i++;
      }
      currentLine.push(field.trim());
      if (currentLine.some(f => f !== '')) {
        lines.push(currentLine);
      }
      currentLine = [];
      field = '';
    } else {
      field += char;
    }
  }
  if (field || currentLine.length > 0) {
    currentLine.push(field.trim());
    lines.push(currentLine);
  }

  if (lines.length < 2) return;

  const headers = lines[0];
  galleryData = lines.slice(1).map(row => {
    const item = {};
    headers.forEach((header, index) => {
      item[header] = row[index] || '';
    });
    return item;
  });

  renderGallery(galleryData);
}

// 외부 CSV 로드 함수
function loadExternalCSV(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = function(e) {
    parseCSV(e.target.result);
  };
  reader.readAsText(file);
}

// 갤러리 그리드 렌더링
function renderGallery(items) {
  const grid = document.getElementById('galleryGrid');
  grid.innerHTML = '';

  items.forEach((item, index) => {
    const card = document.createElement('div');
    card.className = 'card';
    card.onclick = () => openModal(item);

    card.innerHTML = `
      <img src="${item.image}" alt="${item.title}" loading="lazy">
      <div class="card-overlay">
        <div class="card-title">${item.title || 'Untitled'}</div>
        <div class="card-prompt">${item.prompt || ''}</div>
        <div class="card-meta">
          <span>by ${item.author || 'Anonymous'}</span>
          <button class="like-btn" onclick="event.stopPropagation(); addLike(${index}, this)">
            ❤️ ${item.likes || 0}
          </button>
        </div>
      </div>
    `;
    grid.appendChild(card);
  });
}

// 실시간 검색
function handleSearch() {
  const query = document.getElementById('searchInput').value.toLowerCase();
  const filtered = galleryData.filter(item => 
    (item.title && item.title.toLowerCase().includes(query)) ||
    (item.prompt && item.prompt.toLowerCase().includes(query)) ||
    (item.script && item.script.toLowerCase().includes(query)) ||
    (item.tags && item.tags.toLowerCase().includes(query))
  );
  renderGallery(filtered);
}

// 메뉴 열고 접기 토글 및 상위 카테고리 클릭 처리
function toggleMenu(element, categoryTitle) {
  const group = element.parentElement;
  
  // 전체보기 클릭 시 다른 상위 카테고리의 열림 상태 초기화
  document.querySelectorAll('.category-group').forEach(g => {
    if (g !== group) g.classList.remove('open');
  });

  group.classList.toggle('open');

  // 활성화 스타일 적용
  document.querySelectorAll('.sub-item, .category-title').forEach(el => el.classList.remove('active'));
  element.classList.add('active');

  // 상위 카테고리에 속하는 이미지 필터링
  if (categoryTitle && categoryEpMap[categoryTitle]) {
    const targetEps = categoryEpMap[categoryTitle];
    const filtered = galleryData.filter(item => {
      return targetEps.some(ep => 
        (item.category && item.category.includes(ep)) ||
        (item.tags && item.tags.includes(ep)) ||
        (item.title && item.title.includes(ep))
      );
    });
    renderGallery(filtered);
  }
}

// 하위 에피소드 선택 시 필터링 (또는 전체보기 클릭 시)
function filterBySub(epKey, evt, isAll = false) {
  if (evt) evt.stopPropagation();

  document.querySelectorAll('.sub-item, .category-title').forEach(el => el.classList.remove('active'));
  if (evt && evt.target) {
    evt.target.classList.add('active');
  }

  if (isAll || epKey === 'All') {
    // 모든 아코디언 닫기
    document.querySelectorAll('.category-group').forEach(g => g.classList.remove('open'));
    renderGallery(galleryData);
  } else {
    const filtered = galleryData.filter(item => 
      (item.category && item.category.includes(epKey)) ||
      (item.tags && item.tags.includes(epKey)) ||
      (item.title && item.title.includes(epKey))
    );
    renderGallery(filtered);
  }
}

// 좋아요 기능
function addLike(index, btn) {
  let likes = parseInt(galleryData[index].likes || 0);
  likes++;
  galleryData[index].likes = likes;
  btn.innerHTML = `❤️ ${likes}`;
}

// 상세보기 모달 오픈
function openModal(item) {
  document.getElementById('modalImg').src = item.image;
  document.getElementById('modalTitle').innerText = item.title || '제목 없음';
  document.getElementById('modalHook').innerText = item.prompt || '후킹 문구가 없습니다.';
  document.getElementById('modalScript').innerText = item.script || '등록된 대본이 없습니다.';
  document.getElementById('modalTags').innerText = item.tags ? `Tags: ${item.tags}` : '';
  document.getElementById('imageModal').classList.add('active');
}

function closeModal() {
  document.getElementById('imageModal').classList.remove('active');
}