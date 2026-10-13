(() => {
  'use strict';
  const $ = (selector) => document.querySelector(selector);
  const labels = {
    en: {
      navFeatured: 'Selected work', navExplore: 'All projects', navAbout: 'About',
      heroEyebrow: 'Independent engineering & research',
      heroTitle: 'Ideas you<br>can <em>inspect.</em>',
      heroText: 'I build useful software, explore hard questions and publish the work behind the results — from AI systems to physics and interactive visualizations.',
      heroPrimary: 'Explore the projects', heroSecondary: 'About my work',
      manifesto: 'A project is more than a repository. It is a question, a working experiment, and an invitation to look closer.',
      featuredEyebrow: 'A closer look', featuredTitle: 'Selected projects<span class="period">.</span>',
      featuredIntro: 'Some experiments grow into tools. Others remain open questions. These are the stories worth opening first.',
      catalogEyebrow: 'The whole workspace', catalogTitle: 'Explore everything<span class="period">.</span>',
      catalogIntro: 'A living index of public repositories from two GitHub accounts. Updated automatically; curated for humans.',
      showSupport: 'Include supporting repositories and archives', noResults: 'No projects match this search. Try another category or keyword.',
      aboutEyebrow: 'The person behind the work', aboutTitle: 'Science-minded.<br><em>Build-oriented.</em>',
      aboutText: "I'm Dmitry, an engineer and researcher based in Coimbra, Portugal. My background in computational physics shapes how I build software: make assumptions explicit, test ideas, and keep results reproducible.",
      aboutCV: 'CV & experience', backToTop: 'Back to top ↑',
      all: 'All', agents: 'AI & Agents', science: 'Science', visual: 'Visualization', tools: 'Developer tools', experiments: 'Experiments', research: 'Research',
      demo: 'Live demo ↗', video: 'Watch video ↗', source: 'Source ↗', repo: 'GitHub ↗',
      results: (n) => `${n} ${n === 1 ? 'project' : 'projects'}`, synced: (date, count) => `${count} public repos · synced ${date}`, snapshot: (date, count) => `${count} public repos · snapshot ${date}`,
      search: 'Search projects…', loading: 'Loading projects…', loadError: 'Unable to load the catalog. Refresh the page or open the GitHub profiles.',
      archived: 'Archived', support: 'Supporting repo', fork: 'Fork', more: 'Related code', noDescription: 'Public repository — open the source to explore the implementation.', licenseNote: 'Public code does not always come with an open-source license. Check each repository’s license before reusing its code.'
    },
    ru: {
      navFeatured: 'Избранное', navExplore: 'Все проекты', navAbout: 'Обо мне',
      heroEyebrow: 'Независимая разработка и исследования',
      heroTitle: 'Идеи,<br>открытые <em>для всех.</em>',
      heroText: 'Создаю полезные программы, исследую сложные вопросы и публикую результаты — от AI-систем до физики и интерактивных визуализаций.',
      heroPrimary: 'Смотреть проекты', heroSecondary: 'О моей работе',
      manifesto: 'Проект — это больше, чем репозиторий. Это вопрос, работающий эксперимент и приглашение заглянуть глубже.',
      featuredEyebrow: 'Стоит рассмотреть', featuredTitle: 'Избранные проекты<span class="period">.</span>',
      featuredIntro: 'Некоторые эксперименты становятся инструментами. Другие остаются открытыми вопросами. Начать можно с этих.',
      catalogEyebrow: 'Вся коллекция', catalogTitle: 'Все проекты<span class="period">.</span>',
      catalogIntro: 'Живой каталог публичных репозиториев из двух GitHub-аккаунтов. Обновляется автоматически и редактируется вручную.',
      showSupport: 'Показать служебные и архивные репозитории', noResults: 'Ничего не найдено. Попробуйте другой запрос или категорию.',
      aboutEyebrow: 'Об авторе', aboutTitle: 'Научный подход.<br><em>Инженерная практика.</em>',
      aboutText: 'Я Дмитрий, инженер и исследователь из Коимбры, Португалия. Опыт в вычислительной физике определяет мой подход к программированию: явно формулировать предположения, проверять идеи и делать результаты воспроизводимыми.',
      aboutCV: 'Резюме и опыт', backToTop: 'Наверх ↑',
      all: 'Все', agents: 'AI и агенты', science: 'Наука', visual: 'Визуализация', tools: 'Инструменты', experiments: 'Эксперименты', research: 'Исследования',
      demo: 'Открыть демо ↗', video: 'Смотреть видео ↗', source: 'Исходники ↗', repo: 'GitHub ↗',
      results: (n) => `${n} ${plural(n, 'проект', 'проекта', 'проектов')}`, synced: (date, count) => `${count} публичных репозиториев · обновлено ${date}`, snapshot: (date, count) => `${count} публичных репозиториев · снимок ${date}`,
      search: 'Поиск проектов…', loading: 'Загружаю проекты…', loadError: 'Не удалось загрузить каталог. Обновите страницу или откройте профили GitHub.',
      archived: 'Архив', support: 'Служебный', fork: 'Форк', more: 'Связанный код', noDescription: 'Публичный репозиторий — подробности доступны в исходном коде.', licenseNote: 'Публичный код не всегда имеет открытую лицензию. Перед использованием проверьте лицензию каждого репозитория.'
    }
  };
  function plural(n, one, few, many) { return n % 10 === 1 && n % 100 !== 11 ? one : n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 12 || n % 100 > 14) ? few : many; }
  function escapeHtml(v) { return String(v ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch])); }
  function safeUrl(url) { try { const u = new URL(url); return u.protocol === 'https:' ? u.href : ''; } catch { return ''; } }
  function localize(project, field, lang) { return project[`${field}_${lang}`] || project[`${field}_en`] || project[field] || ''; }
  function categoryName(cat) { return labels[state.lang][cat] || labels[state.lang].experiments; }
  function projectDescription(p) { return localize(p, 'summary', state.lang) || p.description || labels[state.lang].noDescription; }
  function projectName(p) { return localize(p, 'title', state.lang) || p.name || p.full_name.split('/').pop().replace(/[-_]/g, ' '); }
  const state = { projects: [], totalRepositories: 0, synced: null, syncSource: 'snapshot', lang: 'en', filter: 'all', search: '', showSupport: false };
  const params = new URLSearchParams(location.search);
  const stored = (() => { try { return localStorage.getItem('portfolio-language'); } catch { return null; } })();
  state.lang = params.get('lang') === 'ru' ? 'ru' : params.get('lang') === 'en' ? 'en' : stored === 'ru' ? 'ru' : 'en';

  function setLanguage(lang, updateUrl = true) {
    state.lang = lang;
    document.documentElement.lang = lang;
    document.title = lang === 'ru' ? 'Дмитрий Глухов — Open Source и исследования' : 'Dmitry Glukhov — Open Source & Research';
    $('[name="description"]').content = lang === 'ru' ? 'Открытые проекты Дмитрия Глухова: AI-агенты, вычислительная физика, интерактивная визуализация и инструменты разработчика.' : 'Open-source software and research projects by Dmitry Glukhov: AI agents, scientific computing, interactive visualizations and developer tools.';
    document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = labels[lang][el.dataset.i18n] || el.textContent; });
    document.querySelectorAll('[data-i18n-html]').forEach(el => { const key = el.dataset.i18nHtml; if (labels[lang][key]) el.innerHTML = labels[lang][key]; });
    $('#language-toggle').textContent = lang === 'en' ? 'RU' : 'EN';
    $('#language-toggle').setAttribute('aria-label', lang === 'en' ? 'Switch to Russian' : 'Переключить на английский');
    $('#project-search').placeholder = labels[lang].search;
    try { localStorage.setItem('portfolio-language', lang); } catch { /* storage disabled */ }
    if (updateUrl) { const u = new URL(location.href); u.searchParams.set('lang', lang); history.replaceState({}, '', u); }
    render();
  }

  function drawFeatured(p, index) {
    const title = escapeHtml(projectName(p));
    const description = escapeHtml(projectDescription(p));
    const repo = safeUrl(p.url);
    const demo = safeUrl(p.demo);
    const cat = p.category || 'experiments';
    const deco = {'agents':'◎','science':'◇','visual':'✳','tools':'⌘','research':'◉','experiments':'∞'}[cat] || '✳';
    const tags = (p.tags || [p.language].filter(Boolean)).slice(0,3);
    return `<article class="featured-card">
      <div class="featured-art art-${escapeHtml(cat)}" aria-hidden="true"><span class="art-index">PROJECT / ${String(index+1).padStart(2,'0')}</span><span class="art-symbol">${deco}</span><span class="art-type">${escapeHtml(categoryName(cat).toUpperCase())}</span></div>
      <div class="featured-body"><div class="card-meta"><span class="card-category">${escapeHtml(categoryName(cat))}</span><span class="meta-dot"></span><span>${escapeHtml((p.language || 'PUBLIC CODE').toUpperCase())}</span></div>
      <h3>${title}</h3><p class="card-copy">${description}</p>
      <div class="card-bottom"><div class="tech-tags">${tags.map(t => `<span class="tech-tag">${escapeHtml(t)}</span>`).join('')}</div><div class="card-links">${demo ? `<a href="${escapeHtml(demo)}" target="_blank" rel="noopener noreferrer">${p.demo_kind === 'video' ? labels[state.lang].video : labels[state.lang].demo}</a>` : ''}<a href="${escapeHtml(repo)}" target="_blank" rel="noopener noreferrer">${labels[state.lang].source}</a></div></div></div>
    </article>`;
  }

  function drawCatalog(p) {
    const relatedCount = (p.related || []).length;
    const repo = safeUrl(p.url);
    const demo = safeUrl(p.demo);
    const cat = p.category || 'experiments';
    const stateTag = p.archived ? labels[state.lang].archived : p.support ? labels[state.lang].support : p.fork ? labels[state.lang].fork : '';
    const related = (p.related || []).map(repo => `<a href="${escapeHtml(safeUrl(repo.url))}" target="_blank" rel="noopener noreferrer">${escapeHtml(repo.full_name.split('/').pop())} ↗</a>`).join('');
    return `<article class="catalog-card">
      <div class="catalog-card-top"><span class="category-pill">${escapeHtml(categoryName(cat))}</span><span class="repo-icon" aria-hidden="true">${{'agents':'◎','science':'◇','visual':'✳','tools':'⌘','research':'◉','experiments':'↗'}[cat] || '↗'}</span></div>
      <h3>${escapeHtml(projectName(p))} ${stateTag ? `<span class="label-small">${escapeHtml(stateTag)}</span>` : ''}</h3>
      <p>${escapeHtml(projectDescription(p))}</p>
      <div class="catalog-card-footer"><div class="language">${escapeHtml(p.language || 'GitHub')}${relatedCount ? ` · +${relatedCount} ${labels[state.lang].more.toLowerCase()}` : ''}</div><div class="links">${demo ? `<a href="${escapeHtml(demo)}" target="_blank" rel="noopener noreferrer">${p.demo_kind === 'video' ? labels[state.lang].video : labels[state.lang].demo}</a>` : ''}<a href="${escapeHtml(repo)}" target="_blank" rel="noopener noreferrer">${labels[state.lang].repo}</a></div></div>
      ${related ? `<details class="related-links"><summary>${labels[state.lang].more} (${p.related.length})</summary><div>${related}</div></details>` : ''}
    </article>`;
  }

  function visibleProjects() {
    const normalized = state.search.trim().toLocaleLowerCase();
    return state.projects.filter(p => {
      if (p.hidden) return false;
      if ((p.support || p.archived) && !state.showSupport) return false;
      if (state.filter !== 'all' && p.category !== state.filter) return false;
      if (!normalized) return true;
      const haystack = [p.full_name, p.name, p.description, p.language, p.category, p.summary_en, p.summary_ru, p.title_en, p.title_ru, ...(p.tags || []), ...(p.topics || [])].filter(Boolean).join(' ').toLocaleLowerCase();
      return haystack.includes(normalized);
    });
  }

  function renderFilters() {
    const categories = ['all','agents','science','visual','tools','research','experiments'];
    $('#category-filters').innerHTML = categories.map(key => `<button type="button" class="filter-btn${state.filter === key ? ' active' : ''}" data-filter="${key}" aria-pressed="${state.filter === key}">${escapeHtml(labels[state.lang][key])}</button>`).join('');
    $('#category-filters').querySelectorAll('[data-filter]').forEach(btn => btn.addEventListener('click', () => { state.filter = btn.dataset.filter; render(); }));
  }
  function render() {
    renderFilters();
    if (!state.projects.length) return;
    const featured = state.projects.filter(p => p.featured_order > 0 && !p.archived && !p.hidden).sort((a,b) => a.featured_order-b.featured_order).slice(0,8);
    $('#featured-grid').innerHTML = featured.length ? featured.map(drawFeatured).join('') : `<p class="loading-state">${labels[state.lang].loading}</p>`;
    const projects = visibleProjects();
    $('#catalog-grid').innerHTML = projects.map(drawCatalog).join('');
    $('#result-count').textContent = labels[state.lang].results(projects.length);
    $('#no-results').hidden = projects.length !== 0;
    if (state.synced) {
      const when = new Date(state.synced);
      const date = Number.isNaN(when.getTime()) ? '' : new Intl.DateTimeFormat(state.lang === 'ru' ? 'ru-RU' : 'en-GB', {day:'numeric',month:'short',year:'numeric',timeZone:'UTC'}).format(when);
      $('#last-sync').textContent = labels[state.lang][state.syncSource === 'github' ? 'synced' : 'snapshot'](date, state.totalRepositories);
    }
  }
  async function loadCatalog() {
    try {
      const response = await fetch('./data/catalog.json', { cache: 'no-cache' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      if (!Array.isArray(data.projects)) throw new Error('Invalid project catalog');
      state.projects = data.projects;
      state.totalRepositories = Number(data.total_repositories) || data.projects.length;
      state.synced = data.generated_at || null;
      state.syncSource = data.sync_source || 'snapshot';
      render();
    } catch (error) {
      console.error('Portfolio catalog failed to load:', error);
      $('#featured-grid').innerHTML = `<p class="loading-state">${labels[state.lang].loadError}</p>`;
      $('#catalog-grid').innerHTML = '';
      $('#result-count').textContent = '';
    }
  }
  $('#language-toggle').addEventListener('click', () => setLanguage(state.lang === 'en' ? 'ru' : 'en'));
  $('#project-search').addEventListener('input', event => { state.search = event.target.value; render(); });
  $('#include-support').addEventListener('change', event => { state.showSupport = event.target.checked; render(); });
  setLanguage(state.lang, false);
  loadCatalog();
})();
