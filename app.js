const lawSelect = document.getElementById('law-select');
const articleInput = document.getElementById('article-num');
const searchBtn = document.getElementById('search-btn');
const resultArea = document.getElementById('result-area');

async function searchArticle() {
    const law = lawSelect.value;
    const num = articleInput.value.trim();
    
    if (!num) return;

    resultArea.innerHTML = '<div class="loader">検索中...</div>';

    try {
        // 1. まずインデックスを取得して、どのファイルにあるか特定
        const idxRes = await fetch(`./data/${law}/index.json`);
        const indexMap = await idxRes.json();
        
        const chunkFile = indexMap[num];
        
        if (!chunkFile) {
            resultArea.innerHTML = '<div class="error">該当する条文が見つかりませんでした。</div>';
            return;
        }

        // 2. 該当するチャンクファイルのみを取得
        const chunkRes = await fetch(`./data/${law}/${chunkFile}`);
        const data = await chunkRes.json();
        const article = data[num];

        // 3. 表示
        renderArticle(article);
    } catch (e) {
        resultArea.innerHTML = '<div class="error">データの取得に失敗しました。</div>';
    }
}

function renderArticle(data) {
    const sentencesHtml = data.s.map(s => `<p class="sentence">${s}</p>`).join('');
    resultArea.innerHTML = `
        <article class="article-card">
            <div class="article-title">${data.t}</div>
            <div class="article-content">${sentencesHtml}</div>
        </article>
    `;
}

searchBtn.addEventListener('click', searchArticle);
articleInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') searchArticle();
});
