// テーマをlocalStorageに永続化する共通ユーティリティ
function initTheme() {
  const saved = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  return saved;
}

function toggleTheme(current) {
  const next = current === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  return next;
}

// 認証付きfetch。401時はログインページへリダイレクト。
async function authFetch(url, options = {}) {
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(url, { ...options, headers });
  if (res.status === 401) {
    localStorage.removeItem('token');
    location.href = '/login.html';
  }
  return res;
}

// JWTトークンを返す（なければログインへ）
function getToken() {
  const token = localStorage.getItem('token');
  if (!token) location.href = '/login.html';
  return token;
}
