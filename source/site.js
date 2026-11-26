/* Majikfingaz Food Villa: shared behaviour for every page */
(function(){
'use strict';
var WA='2348060020861';
var $=function(s,c){return (c||document).querySelector(s)};
var $$=function(s,c){return [].slice.call((c||document).querySelectorAll(s))};
var naira=function(n){return '₦'+Math.round(n).toLocaleString('en-NG')};
var store={get:function(k){try{return JSON.parse(localStorage.getItem(k))}catch(e){return null}},set:function(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}};
function wa(text){window.open('https://wa.me/'+WA+'?text='+encodeURIComponent(text),'_blank','noopener')}
window.MFV={wa:wa,naira:naira};

/* ---------- image slots: drop files into assets/img/<name>.(webp|jpg|png) ---------- */
$$('.ph[data-img]').forEach(function(ph){
  var name=ph.getAttribute('data-img'),exts=['webp','jpg','jpeg','png','avif'],i=0;
  var img=new Image();img.alt=ph.getAttribute('data-alt')||'';img.decoding='async';
  if(ph.getAttribute('data-eager')===null)img.loading='lazy';
  img.onload=function(){ph.classList.add('has-img');ph.dispatchEvent(new Event('mfv:img'))};
  img.onerror=function(){i++;if(i<exts.length)img.src='assets/img/'+name+'.'+exts[i];else img.remove()};
  ph.appendChild(img);
  img.src='assets/img/'+name+'.'+exts[0];
});

/* ---------- mobile nav ---------- */
(function(){
  var tg=$('#menuToggle'),nav=$('#nav');if(!tg||!nav)return;
  tg.addEventListener('click',function(){var o=nav.classList.toggle('open');tg.setAttribute('aria-expanded',o?'true':'false')});
  nav.addEventListener('click',function(e){if(e.target.closest('a')){nav.classList.remove('open');tg.setAttribute('aria-expanded','false')}});
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&nav.classList.contains('open')){nav.classList.remove('open');tg.setAttribute('aria-expanded','false');tg.focus()}});
})();

/* ---------- open / closed in Lagos time ---------- */
var HOURS={0:[12,20],def:[9,21]};
function hrs(d){return HOURS[d]||HOURS.def}
function lab(h){return (h>12?h-12:h)+(h>=12?'pm':'am')}
function lagos(){
  var p=new Intl.DateTimeFormat('en-GB',{timeZone:'Africa/Lagos',weekday:'short',hour:'numeric',minute:'numeric',hour12:false}).formatToParts(new Date()),o={};
  p.forEach(function(x){o[x.type]=x.value});
  return{day:['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].indexOf(o.weekday),mins:(parseInt(o.hour,10)%24)*60+parseInt(o.minute,10)};
}
try{
  var n=lagos(),h=hrs(n.day),isOpen=n.mins>=h[0]*60&&n.mins<h[1]*60,msg;
  if(isOpen)msg='Open now until '+lab(h[1]);
  else{var d=n.mins<h[0]*60?n.day:(n.day+1)%7;msg='Closed now, opens '+(n.mins<h[0]*60?'today':'tomorrow')+' at '+lab(hrs(d)[0])}
  $$('[data-status]').forEach(function(el){el.classList.toggle('closed',!isOpen);var t=$('.t',el);if(t)t.textContent=msg});
  $$('.hours [data-days]').forEach(function(row){
    var ds=row.getAttribute('data-days').split(',').map(Number);if(ds.indexOf(n.day)>-1)row.classList.add('now');
  });
  var td=$('#todayHours');if(td)td.textContent='Today ('+['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'][n.day]+'): '+lab(h[0])+' to '+lab(h[1])+'. '+msg+'.';
}catch(e){}

/* ---------- toast ---------- */
var toastEl,toastT;
function toast(text,actionLabel,action){
  if(!toastEl){toastEl=document.createElement('div');toastEl.className='toast';toastEl.setAttribute('role','status');document.body.appendChild(toastEl)}
  toastEl.innerHTML='';var s=document.createElement('span');s.textContent=text;toastEl.appendChild(s);
  if(actionLabel){var b=document.createElement('button');b.type='button';b.textContent=actionLabel;b.onclick=function(){toastEl.classList.remove('on');action()};toastEl.appendChild(b)}
  toastEl.classList.add('on');clearTimeout(toastT);toastT=setTimeout(function(){toastEl.classList.remove('on')},3600);
}

/* ---------- cart ---------- */
var cart=store.get('mfv-cart')||[];
function save(){store.set('mfv-cart',cart);render();window.dispatchEvent(new Event('mfv:cart'))}
function find(key){for(var i=0;i<cart.length;i++)if(cart[i].key===key)return cart[i]}
function qty(key){var l=find(key);return l?l.qty:0}
function add(item,q){
  var l=find(item.key);
  if(l)l.qty+=q||1;else{item.qty=q||1;cart.push(item)}
  save();
}
function setQty(key,q){
  var l=find(key);if(!l)return;
  if(q<=0)cart=cart.filter(function(x){return x.key!==key});else l.qty=Math.min(q,99);
  save();
}
window.MFV.cart={add:add,setQty:setQty,qty:qty,open:function(){openDrawer()}};

var drawer=$('#drawer'),scrim=$('#scrim'),lastFocus=null;
function totals(){var t=0,est=false;cart.forEach(function(l){t+=l.price*l.qty;if(l.est)est=true});return{t:t,est:est,n:cart.reduce(function(a,l){return a+l.qty},0)}}
function render(){
  var T=totals();
  $$('.cart-btn .count').forEach(function(c){c.textContent=T.n;c.setAttribute('data-n',T.n)});
  $$('.cart-btn').forEach(function(b){b.setAttribute('aria-label','Open your order, '+T.n+' item'+(T.n===1?'':'s'))});
  if(!drawer)return;
  var body=$('#drBody');body.innerHTML='';
  if(!cart.length){body.innerHTML='<div class="dr-empty"><p><b>Your order is empty.</b></p><p>Add dishes from the menu or build a cake and they will appear here.</p><p style="margin-top:16px"><a class="btn btn-plum btn-sm" href="menu.html">Browse the menu</a></p></div>'}
  cart.forEach(function(l){
    var el=document.createElement('div');el.className='line-item';
    el.innerHTML='<h3></h3><div class="amt"></div><div class="sub"></div><div class="ctl"><div class="stepper" role="group"><button type="button" data-d="-1">−</button><output></output><button type="button" data-d="1">+</button></div><button class="rm" type="button">Remove</button></div>';
    var h=$('h3',el);h.textContent=l.name;if(l.est){var e=document.createElement('span');e.className='est';e.textContent='estimate';h.appendChild(e)}
    $('.amt',el).textContent=naira(l.price*l.qty);
    $('.sub',el).textContent=(l.note?l.note+' · ':'')+naira(l.price)+' each';
    var g=$('.stepper',el);g.setAttribute('aria-label','Quantity for '+l.name);
    $('output',el).textContent=l.qty;
    $$('button',g).forEach(function(b){b.setAttribute('aria-label',(b.dataset.d==='1'?'Add one ':'Remove one ')+l.name);b.onclick=function(){setQty(l.key,l.qty+Number(b.dataset.d))}});
    $('.rm',el).setAttribute('aria-label','Remove '+l.name+' from order');
    $('.rm',el).onclick=function(){setQty(l.key,0)};
    body.appendChild(el);
  });
  $('#drTotal').textContent=naira(T.t);
  $('#drEst').hidden=!T.est;
  $('#drSend').disabled=!cart.length;
  $('#drSend').setAttribute('aria-disabled',cart.length?'false':'true');
}
function openDrawer(){
  if(!drawer)return;lastFocus=document.activeElement;
  drawer.removeAttribute('inert');drawer.classList.add('on');scrim.classList.add('on');document.documentElement.style.overflow='hidden';
  setTimeout(function(){$('#drClose').focus()},50);
}
function closeDrawer(){
  if(!drawer||!drawer.classList.contains('on'))return;
  drawer.classList.remove('on');scrim.classList.remove('on');document.documentElement.style.overflow='';
  drawer.setAttribute('inert','');if(lastFocus)lastFocus.focus();
}
if(drawer){
  drawer.setAttribute('inert','');
  $$('.cart-btn').forEach(function(b){b.addEventListener('click',openDrawer)});
  $('#drClose').addEventListener('click',closeDrawer);scrim.addEventListener('click',closeDrawer);
  document.addEventListener('keydown',function(e){
    if(!drawer.classList.contains('on'))return;
    if(e.key==='Escape')closeDrawer();
    if(e.key==='Tab'){
      var f=$$('button:not([disabled]),input,a[href]',drawer).filter(function(x){return x.offsetParent!==null});
      if(!f.length)return;var a=f[0],z=f[f.length-1];
      if(e.shiftKey&&document.activeElement===a){e.preventDefault();z.focus()}
      else if(!e.shiftKey&&document.activeElement===z){e.preventDefault();a.focus()}
    }
  });
  var saved=store.get('mfv-cust')||{};
  if(saved.name)$('#drName').value=saved.name;
  if(saved.mode)($('#drForm input[value="'+saved.mode+'"]')||{}).checked=true;
  $('#drForm').addEventListener('submit',function(e){
    e.preventDefault();if(!cart.length)return;
    var name=$('#drName').value.trim(),mode=$('#drForm input[name=mode]:checked').value,note=$('#drNote').value.trim(),T=totals();
    store.set('mfv-cust',{name:name,mode:mode});
    var L=['Hello Majikfingaz Food Villa, I would like to place an order.',''];
    cart.forEach(function(l){L.push(l.qty+' x '+l.name+(l.note?' ('+l.note+')':'')+(l.est?' [estimate]':'')+' = '+naira(l.price*l.qty))});
    L.push('','Total: '+naira(T.t)+(T.est?' (cake prices are estimates, please confirm)':''));
    L.push('Pickup or delivery: '+mode);
    if(name)L.push('Name: '+name);
    if(note)L.push('Notes: '+note);
    wa(L.join('\n'));
  });
}
render();
window.addEventListener('storage',function(e){if(e.key==='mfv-cart'){cart=store.get('mfv-cart')||[];render();window.dispatchEvent(new Event('mfv:cart'))}});

/* ---------- menu page ---------- */
(function(){
  var grid=$('#dishGrid');if(!grid)return;
  var cards=$$('.dish',grid),cat='all',q='',sort='default',meta=$('#resultMeta'),emptyEl=$('#noResults');
  cards.forEach(function(c,i){c.dataset.i=i});
  function ctl(c){
    var host=$('.ctl',c),key=c.dataset.id,n=qty(key);host.innerHTML='';
    if(!n){
      var b=document.createElement('button');b.type='button';b.className='btn btn-plum btn-sm add';b.innerHTML='<svg class="icon" aria-hidden="true"><use href="#i-plus"/></svg>Add';
      b.setAttribute('aria-label','Add '+c.dataset.name+' to order');
      b.onclick=function(){add({key:key,name:c.dataset.name,price:Number(c.dataset.price)});toast(c.dataset.name+' added','View order',openDrawer)};
      host.appendChild(b);
    }else{
      host.innerHTML='<div class="stepper" role="group"><button type="button" data-d="-1">−</button><output></output><button type="button" data-d="1">+</button></div>';
      var g=$('.stepper',host);g.setAttribute('aria-label','Quantity for '+c.dataset.name);$('output',g).textContent=n;
      $$('button',g).forEach(function(b){b.setAttribute('aria-label',(b.dataset.d==='1'?'Add one ':'Remove one ')+c.dataset.name);b.onclick=function(){setQty(key,qty(key)+Number(b.dataset.d))}});
    }
  }
  function apply(){
    var shown=0,list=cards.slice();
    if(sort==='low')list.sort(function(a,b){return a.dataset.price-b.dataset.price});
    else if(sort==='high')list.sort(function(a,b){return b.dataset.price-a.dataset.price});
    else list.sort(function(a,b){return a.dataset.i-b.dataset.i});
    list.forEach(function(c){
      var ok=(cat==='all'||c.dataset.cat===cat)&&(!q||c.dataset.search.indexOf(q)>-1);
      c.classList.toggle('hide',!ok);if(ok)shown++;grid.appendChild(c);
    });
    meta.textContent=shown+' of '+cards.length+' dishes'+(cat!=='all'?' in '+$('.chipf[aria-pressed=true]').dataset.label:'')+(q?' matching “'+q+'”':'');
    emptyEl.hidden=shown>0;
    if(window.__animateCards)window.__animateCards(grid);
  }
  $$('.chipf').forEach(function(b){
    var n=b.dataset.cat==='all'?cards.length:cards.filter(function(c){return c.dataset.cat===b.dataset.cat}).length;
    b.innerHTML=b.dataset.label+'<span class="n">'+n+'</span>';
    b.onclick=function(){$$('.chipf').forEach(function(x){x.setAttribute('aria-pressed','false')});b.setAttribute('aria-pressed','true');cat=b.dataset.cat;apply()};
  });
  var si=$('#dishSearch'),t;
  si.addEventListener('input',function(){clearTimeout(t);t=setTimeout(function(){q=si.value.trim().toLowerCase();apply()},120)});
  $('#dishSort').addEventListener('change',function(e){sort=e.target.value;apply()});
  $('#clearFilters').addEventListener('click',function(){si.value='';q='';cat='all';$$('.chipf').forEach(function(x){x.setAttribute('aria-pressed',x.dataset.cat==='all'?'true':'false')});apply();si.focus()});
  cards.forEach(ctl);window.addEventListener('mfv:cart',function(){cards.forEach(ctl)});
  /* deep link: menu.html#soups */
  var hv=location.hash.replace('#','');var pre=$('.chipf[data-cat="'+hv+'"]');if(pre)pre.click();else apply();
})();

/* ---------- home: quick add ---------- */
(function(){
  $$('[data-quick]').forEach(function(b){
    b.addEventListener('click',function(){add({key:b.dataset.id,name:b.dataset.name,price:Number(b.dataset.price)});toast(b.dataset.name+' added','View order',openDrawer)});
  });
})();

/* ---------- cake builder ---------- */
(function(){
  var f=$('#builder');if(!f)return;
  var SIZE={s:{m:.75,l:'Small',sv:'about 10 slices'},m:{m:1,l:'Standard',sv:'about 16 slices'},l:{m:1.35,l:'Large',sv:'about 25 slices'},x:{m:1.8,l:'Party',sv:'about 40 slices'}};
  var TYPE={choc:{n:'Signature Chocolate',p:35000,c:'#4A2A1A',c2:'#6B3F2A'},straw:{n:'Strawberry Cream',p:28000,c:'#F2B3C0',c2:'#E07A94'},red:{n:'Red Velvet Dream',p:30000,c:'#9B1B30',c2:'#C0344C'}};
  var FROST={plum:'#6A1B86',leaf:'#66A80F',amber:'#E0902A',cream:'#FFF6E6'};
  var FROSTN={plum:'Plum purple',leaf:'Leaf green',amber:'Amber gold',cream:'Cream white'};
  var FIN={classic:'Classic buttercream',fruit:'Fresh fruit topping',gold:'Edible gold leaf'};
  var d=new Date();d.setDate(d.getDate()+2);
  var dateEl=$('#cDate');dateEl.min=d.toISOString().slice(0,10);
  function val(n){return f.elements[n].value}
  var cur={};
  function update(){
    var t=TYPE[val('type')],s=SIZE[val('size')],fr=FROST[val('frost')],msg=val('msg').trim().slice(0,28);
    var price=Math.round(t.p*s.m/500)*500;cur={type:val('type'),name:t.n+' Cake, '+s.l,price:price,msg:msg,frost:FROSTN[val('frost')],fin:FIN[val('fin')],size:s.l};
    $('#pvName').textContent=t.n+' Cake';
    $('#pvSize').textContent=s.l+', '+s.sv;
    $('#pvFrost').textContent=FROSTN[val('frost')];
    $('#pvFin').textContent=FIN[val('fin')];
    $('#pvMsg').textContent=msg?'“'+msg+'”':'None';
    $('#pvPrice').textContent=naira(price);
    $('#msgCount').textContent=msg.length+'/28';
    var sc={s:.78,m:.92,l:1.05,x:1.16}[val('size')];
    $$('.tier').forEach(function(el,i){el.style.fill=i===0?t.c:t.c2});
    $('#cakeScale').setAttribute('transform','translate(150 215) scale('+sc+') translate(-150 -215)');
    $$('.drip').forEach(function(el){el.style.fill=fr});
    $('#plaqueTxt').textContent=msg||'Congratulations';
    $('#fruit').style.display=val('fin')==='fruit'?'block':'none';
    $('#gold').style.display=val('fin')==='gold'?'block':'none';
  }
  f.addEventListener('input',update);f.addEventListener('change',update);update();
  f.addEventListener('submit',function(e){e.preventDefault()});
  function note(){return [cur.frost+' frosting',cur.fin,cur.msg?'message: '+cur.msg:null,dateEl.value?'needed '+dateEl.value:null].filter(Boolean).join(', ')}
  $('#cAdd').addEventListener('click',function(){
    add({key:'cake-'+cur.name+'|'+note(),name:cur.name,price:cur.price,est:true,note:note()});
    toast('Cake added to your order','View order',openDrawer);
  });
  $('#cWa').addEventListener('click',function(){
    wa(['Hello Majikfingaz Food Villa, I would like to order a custom cake.','',
      'Cake: '+cur.name,'Frosting: '+cur.frost,'Finish: '+cur.fin,'Message on cake: '+(cur.msg||'none'),
      'Date needed: '+(dateEl.value||'not set yet'),'Estimated price: '+naira(cur.price),'','Please confirm availability and the final price.'].join('\n'));
  });
})();

/* ---------- catering estimator ---------- */
(function(){
  var f=$('#estimator');if(!f)return;
  var g=f.elements.guests,out=$('#estOut');
  var ITEMS={jollof:['Party jollof rice','portions',1.1],fried:['Fried rice','portions',1.1],soup:['Soup and swallow','portions',1.05],protein:['Protein (chicken, goat or fish)','pieces',1.1],chops:['Small chops','pieces',6],drinks:['Drinks','bottles or cups',2]};
  function calc(){
    var n=Number(g.value);$('#gVal').textContent=n;g.setAttribute('aria-valuetext',n+' guests');
    var rows=[];
    $$('input[name=item]:checked',f).forEach(function(c){var it=ITEMS[c.value];rows.push([it[0],Math.ceil(n*it[2]),it[1],c.value])});
    out.innerHTML='';
    if(!rows.length){out.innerHTML='<div><span>Tick what you would like to serve to see quantities.</span></div>';return}
    rows.forEach(function(r){var d=document.createElement('div');d.innerHTML='<span></span><b></b>';$('span',d).textContent=r[0];$('b',d).textContent=r[1].toLocaleString('en-NG')+' '+r[2];out.appendChild(d)});
    var p=document.createElement('p');p.className='fine';p.textContent='A planning guide with a small buffer so nobody runs short. We confirm real quantities and price when you send this.';out.appendChild(p);
    f._rows=rows;
  }
  f.addEventListener('input',calc);calc();
  f.addEventListener('submit',function(e){
    e.preventDefault();calc();
    var L=['Hello Majikfingaz Food Villa, I would like a catering quote.',''];
    L.push('Event: '+f.elements.event.value,'Guests: '+g.value);
    if(f.elements.date.value)L.push('Date: '+f.elements.date.value);
    if(f.elements.area.value.trim())L.push('Venue or area: '+f.elements.area.value.trim());
    if(f._rows&&f._rows.length){L.push('','Menu and rough quantities:');f._rows.forEach(function(r){L.push('- '+r[0]+': '+r[1]+' '+r[2])})}
    wa(L.join('\n'));
  });
})();

/* ---------- gallery + lightbox ---------- */
(function(){
  var gal=$('#gallery');if(!gal)return;
  var items=$$('.gi',gal),lb=$('#lb'),cur=0,vis=[],last=null;
  $$('.chipf').forEach(function(b){
    b.onclick=function(){
      $$('.chipf').forEach(function(x){x.setAttribute('aria-pressed','false')});b.setAttribute('aria-pressed','true');
      items.forEach(function(i){i.classList.toggle('hide',b.dataset.cat!=='all'&&i.dataset.cat!==b.dataset.cat)});
      if(window.__animateCards)window.__animateCards(gal,'.gi');
    };
  });
  function list(){vis=items.filter(function(i){return !i.classList.contains('hide')})}
  function show(i){
    list();cur=(i+vis.length)%vis.length;var it=vis[cur],ph=$('.ph',it);
    var slot=$('#lbSlot');slot.setAttribute('data-img',ph.getAttribute('data-img'));slot.className='ph r43';slot.innerHTML='<span class="ph-label"></span>';
    $('.ph-label',slot).textContent=it.dataset.cap;
    var src=$('img',ph);if(src){var c=new Image();c.src=src.src;c.alt=src.alt;slot.appendChild(c);slot.classList.add('has-img')}
    $('#lbCap').textContent=it.dataset.cap;$('#lbCount').textContent=(cur+1)+' / '+vis.length;
  }
  function open(i){last=document.activeElement;lb.classList.add('on');document.documentElement.style.overflow='hidden';show(i);$('#lbClose').focus()}
  function close(){lb.classList.remove('on');document.documentElement.style.overflow='';if(last)last.focus()}
  items.forEach(function(it){it.addEventListener('click',function(){list();open(vis.indexOf(it))})});
  $('#lbClose').onclick=close;$('#lbPrev').onclick=function(){show(cur-1)};$('#lbNext').onclick=function(){show(cur+1)};
  lb.addEventListener('click',function(e){if(e.target===lb)close()});
  document.addEventListener('keydown',function(e){
    if(!lb.classList.contains('on'))return;
    if(e.key==='Escape')close();if(e.key==='ArrowRight')show(cur+1);if(e.key==='ArrowLeft')show(cur-1);
    if(e.key==='Tab'){var f=$$('button',lb),a=f[0],z=f[f.length-1];if(e.shiftKey&&document.activeElement===a){e.preventDefault();z.focus()}else if(!e.shiftKey&&document.activeElement===z){e.preventDefault();a.focus()}}
  });
  var sx=null;lb.addEventListener('touchstart',function(e){sx=e.touches[0].clientX},{passive:true});
  lb.addEventListener('touchend',function(e){if(sx===null)return;var dx=e.changedTouches[0].clientX-sx;if(Math.abs(dx)>50)show(cur+(dx<0?1:-1));sx=null});
})();

/* ---------- contact form ---------- */
(function(){
  var f=$('#contactForm');if(!f)return;
  function bad(el,msg){el.setAttribute('aria-invalid','true');var e=el.parentNode.querySelector('.err');if(e)e.textContent=msg;return false}
  function ok(el){el.removeAttribute('aria-invalid');var e=el.parentNode.querySelector('.err');if(e)e.textContent=''}
  f.addEventListener('submit',function(e){
    e.preventDefault();var good=true,n=f.elements.name,m=f.elements.message;
    ok(n);ok(m);
    if(!n.value.trim())good=bad(n,'Please tell us your name.');
    if(!m.value.trim())good=bad(m,'Please write a short message.')&&good;
    if(!good){var first=$('[aria-invalid=true]',f);if(first)first.focus();return}
    wa(['Hello Majikfingaz Food Villa,','Topic: '+f.elements.topic.value,'Name: '+n.value.trim(),f.elements.phone.value.trim()?'Phone: '+f.elements.phone.value.trim():null,'','Message: '+m.value.trim()].filter(function(x){return x!==null}).join('\n'));
  });
  $$('details',$('.faq')).forEach(function(d){d.addEventListener('toggle',function(){if(d.open)$$('details',$('.faq')).forEach(function(o){if(o!==d)o.open=false})})});
})();

/* ---------- catering quote form (home/catering) ---------- */
(function(){
  var f=$('#quoteForm');if(!f)return;
  f.addEventListener('submit',function(e){
    e.preventDefault();var L=['Hello Majikfingaz Food Villa, I would like a catering quote.','Event: '+f.event.value];
    if(f.guests.value)L.push('Guests: '+f.guests.value);if(f.date.value)L.push('Date: '+f.date.value);if(f.area.value.trim())L.push('Location: '+f.area.value.trim());wa(L.join('\n'));
  });
})();

var y=$('#year');if(y)y.textContent=new Date().getFullYear();
})();

/* ---------- motion: GSAP + ScrollTrigger (content stays visible if unavailable or reduced) ---------- */
(function(){
  if(!window.gsap||!window.ScrollTrigger)return;
  gsap.registerPlugin(ScrollTrigger);
  var $=function(s,c){return [].slice.call((c||document).querySelectorAll(s))};
  function split(el){
    var t=el.textContent.trim().replace(/\s+/g,' ');el.setAttribute('aria-label',t);
    el.innerHTML=t.split(' ').map(function(w){return '<span class="w" aria-hidden="true"><span>'+w+'</span></span>'}).join(' ');
    return $('.w>span',el);
  }
  $('.card,.tile').forEach(function(c){c.addEventListener('pointermove',function(e){var r=c.getBoundingClientRect();c.style.setProperty('--mx',(e.clientX-r.left)+'px');c.style.setProperty('--my',(e.clientY-r.top)+'px')})});
  var header=$('.header')[0];
  function onScroll(){header.classList.toggle('scrolled',window.scrollY>8)}
  window.addEventListener('scroll',onScroll,{passive:true});onScroll();
  var marquee=document.getElementById('marquee'),mtween=null,paused=false;
  var mm=gsap.matchMedia();
  mm.add('(prefers-reduced-motion: no-preference)',function(){
    var h1=$('.hero h1,.phero h1')[0];
    if(h1){
      var words=split(h1),tl=gsap.timeline({defaults:{ease:'expo.out'}});
      tl.from('.hero .status,.crumbs',{y:16,opacity:0,duration:.7},.05)
        .from(words,{yPercent:115,duration:1.1,stagger:.07},.15)
        .from('.hero .lede,.phero .lede',{y:22,opacity:0,duration:.8},.6)
        .from('.hero .actions .btn',{y:22,opacity:0,duration:.7,stagger:.1,clearProps:'transform,opacity'},.8)
        .from('.hero-art .ph,.phero .ph',{scale:.9,opacity:0,rotate:-2,duration:1.2},.2)
        .from('.chip',{y:34,opacity:0,scale:.88,duration:.8,stagger:.14,ease:'back.out(1.6)'},.95);
      $('.chip').forEach(function(c,i){gsap.to(c,{y:i%2?10:-10,duration:2.8+i*.5,repeat:-1,yoyo:true,ease:'sine.inOut',delay:1.6})});
    }
    gsap.to('.progress',{scaleX:1,ease:'none',scrollTrigger:{start:0,end:'max',scrub:.25}});
    $('.sec-head h2,.cta h2,.split h2,.catering h2').forEach(function(h){
      var w=split(h);gsap.fromTo(w,{yPercent:115},{yPercent:0,duration:1,stagger:.06,ease:'expo.out',immediateRender:false,scrollTrigger:{trigger:h,start:'top 88%',once:true}});
    });
    function batchIn(sel,from){
      if(!$(sel).length)return;
      ScrollTrigger.batch(sel,{start:'top 92%',once:true,onEnter:function(b){gsap.fromTo(b,from,{opacity:1,x:0,y:0,duration:.8,stagger:.1,ease:'power3.out',overwrite:true,immediateRender:false,clearProps:'transform,opacity'})}});
    }
    batchIn('.sec-head p',{opacity:0,y:18});batchIn('.facts li',{opacity:0,y:22});batchIn('.tile',{opacity:0,y:40});
    batchIn('.how li',{opacity:0,y:30});batchIn('.val',{opacity:0,y:34});batchIn('.stats div',{opacity:0,y:20});
    batchIn('.pkg article',{opacity:0,y:34});batchIn('.steps li',{opacity:0,x:-30});batchIn('.panel',{opacity:0,y:32});
    batchIn('.bstep',{opacity:0,y:28});batchIn('.faq details',{opacity:0,y:18});batchIn('.split .ph',{opacity:0,scale:.94});
    batchIn('.cakes-grid .card',{opacity:0,y:40});
    $('.band-strip,.catering .band').forEach(function(b){
      gsap.set(b,{backgroundPosition:'0px 0px'});
      gsap.to(b,{backgroundPosition:'-288px 0px',ease:'none',scrollTrigger:{trigger:b,start:'top bottom',end:'bottom top',scrub:true}});
    });
    window.__animateCards=function(panel,sel){
      gsap.fromTo($(sel||'.card:not(.hide)',panel).filter(function(e){return !e.classList.contains('hide')}),{opacity:0,y:22},{opacity:1,y:0,duration:.5,stagger:.05,ease:'power2.out',overwrite:true,clearProps:'transform,opacity'});
    };
    if(window.matchMedia('(hover:hover) and (pointer:fine)').matches){
      $('[data-magnet]').forEach(function(el){
        var xt=gsap.quickTo(el,'x',{duration:.5,ease:'power3'}),yt=gsap.quickTo(el,'y',{duration:.5,ease:'power3'});
        el.addEventListener('pointermove',function(e){var r=el.getBoundingClientRect();xt((e.clientX-r.left-r.width/2)*.22);yt((e.clientY-r.top-r.height/2)*.32)});
        el.addEventListener('pointerleave',function(){xt(0);yt(0)});
      });
    }
    /* count-up stats */
    $('[data-count]').forEach(function(el){
      var to=Number(el.dataset.count),o={v:0},suf=el.dataset.suffix||'';
      ScrollTrigger.create({trigger:el,start:'top 90%',once:true,onEnter:function(){gsap.to(o,{v:to,duration:1.6,ease:'power2.out',onUpdate:function(){el.textContent=Math.round(o.v)+suf}})}});
    });
    /* cake preview gentle float */
    if($('.cake-art svg').length)gsap.to('.cake-art svg',{y:-6,duration:2.6,repeat:-1,yoyo:true,ease:'sine.inOut'});
    /* ticker */
    if(marquee){
      var track=marquee.querySelector('.marquee-track'),group=marquee.querySelector('.marquee-group'),toggle=document.getElementById('marqueeToggle');
      var build=function(){if(mtween)mtween.kill();gsap.set(track,{x:0});var w=group.offsetWidth;mtween=gsap.to(track,{x:-w,duration:w/70,ease:'none',repeat:-1});if(paused)mtween.pause()};
      build();var rt;window.addEventListener('resize',function(){clearTimeout(rt);rt=setTimeout(build,200)});
      if(document.fonts&&document.fonts.ready)document.fonts.ready.then(build);
      marquee.addEventListener('pointerenter',function(){if(mtween&&!paused)mtween.pause()});
      marquee.addEventListener('pointerleave',function(){if(mtween&&!paused)mtween.resume()});
      toggle.addEventListener('click',function(){paused=!paused;toggle.textContent=paused?'Play':'Pause';toggle.setAttribute('aria-pressed',paused?'true':'false');if(mtween)paused?mtween.pause():mtween.resume()});
    }
    return function(){if(mtween)mtween.kill()};
  });
  mm.add('(prefers-reduced-motion: reduce)',function(){if(marquee)marquee.classList.add('static')});
})();
