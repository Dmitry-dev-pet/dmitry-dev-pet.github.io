(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const NS = 'http://www.w3.org/2000/svg';
  const pageSize = 30;
  const state = {records:[], byArchive:{}, visible:[], selected:null, page:0};

  function safeUrl(s) {
    try {
      if (typeof s !== 'string' || s.length > 800 || /[<>\r\n]/.test(s)) return null;
      const u = new URL(s, location.href);
      if (!['http:', 'https:'].includes(u.protocol) || u.username || u.password) return null;
      if (!u.hostname.includes('.') || /(^localhost$|\.local$|^127\.|^10\.|^192\.168\.|^169\.254\.)/i.test(u.hostname)) return null;
      if (/(^|\.)drive\.google\.com$|(^|\.)githubusercontent\.com$/i.test(u.hostname)) return null;
      if (u.hostname === 'github.com' && u.pathname.toLowerCase().startsWith('/dmitry-dev-pet/nevzorov-lab')) return null;
      for (const key of ['token','access_token','api_key','auth','signature','key']) if (u.searchParams.has(key)) return null;
      return u.href;
    } catch (_) { return null; }
  }
  function lower(s) { return String(s||'').toLocaleLowerCase('ru').trim(); }
  function html(tag, value, cls) {
    const e=document.createElement(tag);
    if(value!==undefined)e.textContent=value;
    if(cls)e.className=cls;
    return e;
  }
  function svg(tag, props, value) {
    const e=document.createElementNS(NS,tag);
    for(const [k,v] of Object.entries(props||{}))e.setAttribute(k,String(v));
    if(value!==undefined)e.textContent=value;
    return e;
  }
  function archives(row) {return state.byArchive[row.id]||[];}
  function relation(row) {
    if(row.relation==='identity_recorded')return 'Связана с частной копией';
    if(row.relation==='partial_or_related')return 'Есть частичный либо смежный материал';
    return 'Привязка к сохранённой работе не установлена';
  }
  function makeLink(href,title,note) {
    const link=safeUrl(href);if(!link)return null;
    const a=html('a',title);a.href=link;a.target='_blank';a.rel='noopener noreferrer';
    if(note)a.appendChild(html('small',note));
    return a;
  }
  function match(row) {
    const q=lower($('search').value),s=$('status').value,f=$('links').value;
    if(q&&!lower([row.id,row.citation,...archives(row).map(x=>x.title)].join(' ')).includes(q))return false;
    if(s==='confirmed'&&row.identification!=='confirmed')return false;
    if(s==='candidate'&&row.identification!=='candidate')return false;
    if(s==='linked'&&row.relation!=='identity_recorded')return false;
    if(s==='partial'&&row.relation!=='partial_or_related')return false;
    if(s==='missing'&&row.relation!=='not_established')return false;
    if(f==='catalog'&&!safeUrl(row.catalog_url))return false;
    if(f==='viewer'&&!safeUrl(row.viewer_url))return false;
    if(f==='archive'&&!archives(row).length)return false;
    return true;
  }
  function filtersChanged() {
    state.page=0;state.visible=state.records.filter(match);
    if(!state.visible.some(r=>r.id===state.selected))state.selected=state.visible[0]?.id||null;
    update();
  }
  function select(id) {
    if(!state.records.some(r=>r.id===id))return;
    state.selected=id;
    const idx=state.visible.findIndex(r=>r.id===id);
    if(idx>=0)state.page=Math.floor(idx/pageSize);
    const url=new URL(location.href);url.searchParams.set('bib',id);
    history.replaceState(null,'',url.pathname+url.search);
    update();
  }
  function update() {
    $('count').textContent=state.visible.length+' из '+state.records.length+' записей';
    const start=state.page*pageSize,shown=state.visible.slice(start,start+pageSize);
    const list=$('results');list.replaceChildren();
    if(!shown.length)list.appendChild(html('p','Ничего не найдено.','help'));
    for(const row of shown) {
      const btn=html('button',undefined,'result');btn.type='button';btn.setAttribute('role','option');
      btn.setAttribute('aria-selected',String(row.id===state.selected));
      btn.appendChild(html('div','NV-BIB2013-CUR-'+row.id,'rid'));
      btn.appendChild(html('div',row.citation,'citation'));
      const p=html('div',undefined,'pills');
      p.appendChild(html('span',row.identification==='confirmed'?'Идентифицировано':'Кандидат','pill'));
      if(row.relation==='identity_recorded')p.appendChild(html('span','Есть частная копия','pill'));
      if(archives(row).length)p.appendChild(html('span','Архив: '+archives(row).length,'pill'));
      btn.appendChild(p);btn.addEventListener('click',()=>select(row.id));list.appendChild(btn);
    }
    $('page-label').textContent=state.visible.length?(start+1)+'–'+Math.min(start+pageSize,state.visible.length)+' из '+state.visible.length:'Нет совпадений';
    $('prev').disabled=state.page===0;$('next').disabled=(state.page+1)*pageSize>=state.visible.length;
    showDetail();
  }
  function curve(layer,x1,y1,x2,y2) {
    const mid=(y1+y2)/2;
    layer.appendChild(svg('path',{d:'M'+x1+','+y1+' C'+x1+','+mid+' '+x2+','+mid+' '+x2+','+y2,class:'graph-line'}));
  }
  function node(layer,cfg) {
    const g=svg('g');
    g.appendChild(svg('rect',{x:cfg.x-cfg.w/2,y:cfg.y-cfg.h/2,width:cfg.w,height:cfg.h,rx:11,class:'graph-node '+cfg.type}));
    g.appendChild(svg('text',{x:cfg.x-cfg.w/2+12,y:cfg.y-cfg.h/2+19,class:'svg-type'},cfg.tag));
    const words=String(cfg.title).split(/\s+/),lines=[''];
    for(const word of words){
      const k=lines.length-1,tryLine=(lines[k]?lines[k]+' ':'')+word;
      if(tryLine.length>28&&lines[k]&&lines.length<2)lines.push(word);
      else if(tryLine.length>30)lines[k]=tryLine.slice(0,27)+'…';
      else lines[k]=tryLine;
    }
    lines.slice(0,2).forEach((t,i)=>g.appendChild(svg('text',{x:cfg.x-cfg.w/2+12,y:cfg.y-cfg.h/2+37+i*15,class:'svg-label'},t)));
    if(cfg.sub)g.appendChild(svg('text',{x:cfg.x-cfg.w/2+12,y:cfg.y+cfg.h/2-10,class:'svg-caption'},cfg.sub.slice(0,35)));
    layer.appendChild(g);
  }
  function draw(row) {
    const lines=$('graph-lines'),nodes=$('graph-nodes');lines.replaceChildren();nodes.replaceChildren();
    const book={x:430,y:58,w:300,h:65,type:'book',tag:'ИСТОЧНИК',title:'Книга Невзорова (2013)'};
    const entry={x:430,y:183,w:320,h:91,type:'entry',tag:'СТРОКА БИБЛИОГРАФИИ',title:'№ '+row.id+' · '+(row.identification==='confirmed'?'идентифицирована':'кандидат'),sub:'Упоминание не означает чтение'};
    curve(lines,430,90,430,138);node(nodes,book);node(nodes,entry);
    const slots=[
      {show:!!safeUrl(row.catalog_url),x:145,tag:'ВНЕШНИЙ КАТАЛОГ',title:'Библиографическая карточка',type:'catalog',sub:'Указатель не равен оригиналу'},
      {show:!!safeUrl(row.viewer_url),x:430,tag:'ВНЕШНИЙ ПРОСМОТР',title:'Просмотр текста',type:'viewer',sub:'Сверяйте полноту страниц'},
      {show:archives(row).length>0,x:715,tag:'ОТКРЫТЫЕ АРХИВЫ',title:'Архивных ссылок: '+archives(row).length,type:'archive',sub:'Сверяйте год и издание'}
    ];
    for(const slot of slots) {
      if(!slot.show)continue;
      curve(lines,430,229,slot.x,310);
      node(nodes,{x:slot.x,y:355,w:250,h:90,type:slot.type,tag:slot.tag,title:slot.title,sub:slot.sub});
    }
    if(row.relation!=='not_established'){
      curve(lines,430,229,430,437);
      node(nodes,{x:430,y:476,w:300,h:65,type:'copy',tag:'СТАТУС ПРИВАТНОГО КОРПУСА',title:row.relation==='identity_recorded'?'Сохранённая частная копия':'Смежная / частичная работа',sub:'Сам файл через сайт не раздаётся'});
    }
  }
  function showDetail() {
    const row=state.records.find(x=>x.id===state.selected);
    const panel=$('detail');panel.replaceChildren();
    if(!row){$('graph-lines').replaceChildren();$('graph-nodes').replaceChildren();panel.appendChild(html('p','Выберите строку библиографии.','help'));return;}
    draw(row);
    panel.appendChild(html('div','NV-BIB2013-CUR-'+row.id,'rid'));
    panel.appendChild(html('h3',row.citation));
    const badges=html('div',undefined,'statusline');
    badges.appendChild(html('span',row.identification==='confirmed'?'Библиографически идентифицирована':'Библиографическая запись требует проверки','flag'));
    badges.appendChild(html('span',relation(row),'flag'));panel.appendChild(badges);
    panel.appendChild(html('div','Открытые источники','key'));
    const list=html('div',undefined,'linklist');
    const catalog=makeLink(row.catalog_url,'Каталог / источник идентификации','Не обязательно содержит полный текст');
    if(catalog)list.appendChild(catalog);
    if(row.viewer_url!==row.catalog_url){const viewer=makeLink(row.viewer_url,'Путь к просмотру текста',row.viewer_status||'Полнота не установлена');if(viewer)list.appendChild(viewer);}
    for(const a of archives(row)){
      const flag=a.relation_status==='exact_work_claimed_in_manifest'?'Связана с работой по реестру':'Связанная работа, издание требуется сверить';
      const link=makeLink(a.url,a.title||'Архивный экземпляр',(a.year?'Год '+a.year+' · ':'')+flag);
      if(link)list.appendChild(link);
    }
    if(list.children.length)panel.appendChild(list);else panel.appendChild(html('p','Публичный адрес этой работы пока не установлен.','info muted'));
    panel.appendChild(html('div','Границы проверки','key'));
    panel.appendChild(html('p',relation(row)+'. Связанных PDF: '+row.saved_pdf_count+'. Статус издания: '+row.edition_status+'. Приватные копии не публикуются.','info muted'));
    panel.appendChild(html('p','Ссылка на каталог или архив не доказывает доступность полного текста, совпадение конкретного издания или факт чтения его Невзоровым.','info muted'));
  }
  function ingestArchives(files) {
    for(const doc of files){
      if(doc.schema_version!==1)throw Error('Unknown archive schema');
      for(const [id,links] of Object.entries(doc.by_bib||{})){
        if(!/^\d{4}$/.test(id)||!Array.isArray(links))continue;
        const arr=state.byArchive[id]||(state.byArchive[id]=[]);
        for(const item of links)if(safeUrl(item.url)&&!arr.some(x=>x.url===item.url))arr.push(item);
      }
    }
  }
  async function load(path){
    const r=await fetch(path,{cache:'no-cache',credentials:'omit'});
    if(!r.ok)throw Error(path+' HTTP '+r.status);
    return r.json();
  }
  async function init() {
    try{
      const [bib,a,b]=await Promise.all([load('bibliography.json'),load('archives-a.json'),load('archives-b.json')]);
      if(bib.schema_version!==1||bib.records?.length!==456||new Set(bib.records.map(x=>x.id)).size!==456)throw Error('Invalid bibliography payload');
      state.records=bib.records;ingestArchives([a,b]);
      $('stat-total').textContent=state.records.length;
      $('stat-confirmed').textContent=state.records.filter(x=>x.identification==='confirmed').length;
      $('stat-linked').textContent=state.records.filter(x=>x.relation==='identity_recorded').length;
      $('stat-archive').textContent=Object.values(state.byArchive).reduce((n,x)=>n+x.length,0);
      state.visible=state.records.slice();
      const initial=new URL(location.href).searchParams.get('bib');
      select(state.records.some(x=>x.id===initial)?initial:state.records[0].id);
    }catch(e){
      $('count').textContent='Не удалось получить данные';
      $('detail').replaceChildren(html('p','Публичный каталог временно недоступен. Обновите страницу.','info'));
      console.warn('Bibliography data load:',e);
    }
  }
  $('search').addEventListener('input',filtersChanged);
  $('status').addEventListener('change',filtersChanged);
  $('links').addEventListener('change',filtersChanged);
  $('prev').addEventListener('click',()=>{state.page=Math.max(0,state.page-1);update();});
  $('next').addEventListener('click',()=>{state.page=Math.min(Math.floor((state.visible.length-1)/pageSize),state.page+1);update();});
  init();
})();
