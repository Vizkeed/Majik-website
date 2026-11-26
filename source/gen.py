import re, pathlib, html, json, shutil
HERE = pathlib.Path(__file__).resolve().parent
R = HERE.parent
OUT = R / 'public'
SYMS = (HERE / 'symbols.svg.txt').read_text()
SYMS += ('<symbol id="i-plus" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></symbol>'
         '<symbol id="i-cart" viewBox="0 0 24 24"><circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M2 3h3l2.6 12.4a2 2 0 0 0 2 1.6h7.8a2 2 0 0 0 2-1.5L21 7H6"/></symbol>'
         '<symbol id="i-search" viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></symbol>'
         '<symbol id="i-x" viewBox="0 0 24 24"><path d="M18 6 6 18M6 6l12 12"/></symbol>'
         '<symbol id="i-left" viewBox="0 0 24 24"><path d="m15 18-6-6 6-6"/></symbol>'
         '<symbol id="i-right" viewBox="0 0 24 24"><path d="m9 18 6-6-6-6"/></symbol>')
E = html.escape
SLOTS = {}

def ic(n, cls='icon'):
    return f'<svg class="{cls}" aria-hidden="true"><use href="#i-{n}"/></svg>'

def slot(name, label, alt, ratio='r43', pat='a', extra='', eager=False):
    SLOTS[name] = (label, ratio)
    e = ' data-eager' if eager else ''
    return (f'<div class="ph {ratio} pat-{pat} {extra}" data-img="{name}" data-alt="{E(alt)}"{e}>'
            f'<span class="ph-label">{E(label)}</span></div>')

NAV = [('index.html', 'Home'), ('menu.html', 'Menu'), ('cakes.html', 'Cakes'), ('catering.html', 'Catering'),
       ('gallery.html', 'Gallery'), ('about.html', 'About'), ('contact.html', 'Contact')]

def head(title, desc, extra=''):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="theme-color" content="#6A1B86">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<link rel="icon" href="assets/img/logo-mark.webp">
<link rel="preload" href="assets/fonts/bricolage-grotesque-latin-opsz-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/figtree-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/fonts.css">
<link rel="stylesheet" href="assets/site.css">
{extra}</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>{SYMS}</defs></svg>
<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="wrap">
<span class="hrs">Kitchen open Monday to Saturday 9am to 9pm, Sunday 12pm to 8pm</span>
<a href="tel:+2348060020861">Call +234 806 002 0861</a></div></div>
'''

def header(active):
    links = ''.join(f'<a class="link" href="{h}"{" aria-current=\"page\"" if h == active else ""}>{t}</a>' for h, t in NAV)
    return f'''<header class="header"><div class="wrap">
<a class="logo" href="index.html" aria-label="Majikfingaz Food Villa, home"><img src="assets/img/logo-mark.webp" alt="Majikfingaz Food Villa" width="156" height="52"></a>
<nav class="nav" id="nav" aria-label="Main">{links}<a class="btn btn-amber btn-sm" href="menu.html">Order now</a></nav>
<div class="hdr-actions">
<button class="cart-btn" type="button" aria-label="Open your order, 0 items">{ic('cart')}<span class="lbl">Order</span><span class="count" data-n="0">0</span></button>
<button class="menu-toggle" id="menuToggle" aria-expanded="false" aria-controls="nav">Menu</button></div>
</div><div class="progress" aria-hidden="true"></div></header>
<main id="main">
'''

def footer():
    ln = ''.join(f'<li><a href="{h}">{t}</a></li>' for h, t in NAV)
    return f'''</main>
<footer class="footer"><div class="wrap">
<div><span class="logo-card"><img src="assets/img/logo-full.webp" alt="Majikfingaz Food Villa" width="240" height="120"></span>
<p class="tagline">Savor tradition</p>
<p style="margin-top:10px;max-width:26em">Nigerian meals, handcrafted cakes and professional event catering, made with passion in Olodi, Apapa and served across Lagos.</p></div>
<div><h3>Explore</h3><ul>{ln}</ul></div>
<div><h3>Visit and contact</h3><ul>
<li>111 Oba Olu-Iwa Road (111 Kirikiri Road), near Wilmer Bus Stop, Olodi, Apapa, Lagos</li>
<li><a href="tel:+2348060020861">+234 806 002 0861</a></li>
<li><a href="tel:+2349053622980">+234 905 362 2980</a></li>
<li><a href="https://www.instagram.com/majikfingaz_catering" rel="noopener" target="_blank">Instagram @Majikfingaz_catering</a></li>
<li>Mon to Sat 9am to 9pm<br>Sun 12pm to 8pm</li></ul></div>
<p class="legal">&copy; <span id="year">2026</span> Majikfingaz Food Villa. All rights reserved. Crafted with flavour in Lagos, Nigeria.</p>
</div></footer>
<div class="order-bar"><a class="btn btn-amber" href="https://wa.me/2348060020861?text=Hello%20Majikfingaz%20Food%20Villa" target="_blank" rel="noopener">{ic('chat')}Order on WhatsApp</a></div>
<div class="scrim" id="scrim"></div>
<aside class="drawer" id="drawer" role="dialog" aria-modal="true" aria-labelledby="drTitle">
<div class="dr-head"><h2 id="drTitle">Your order</h2><button class="x" id="drClose" type="button" aria-label="Close order">{ic('x')}</button></div>
<div class="dr-body" id="drBody"></div>
<form class="dr-foot" id="drForm">
<div class="seg" role="radiogroup" aria-label="Pickup or delivery"><label><input type="radio" name="mode" value="Pickup" checked><span>Pickup</span></label><label><input type="radio" name="mode" value="Delivery"><span>Delivery</span></label></div>
<input type="text" id="drName" placeholder="Your name" aria-label="Your name" autocomplete="name">
<input type="text" id="drNote" placeholder="Address or notes (optional)" aria-label="Address or notes">
<div class="total"><span>Total</span><b id="drTotal">₦0</b></div>
<small id="drEst" hidden>Cake prices are estimates. We confirm the final price on WhatsApp.</small>
<button class="btn btn-amber" id="drSend" type="submit">{ic('chat')}Send order on WhatsApp</button>
<small>Delivery area and fee are confirmed on WhatsApp.</small>
</form></aside>
<script src="assets/gsap.min.js"></script>
<script src="assets/ScrollTrigger.min.js"></script>
<script src="assets/site.js"></script>
</body></html>
'''

def write(name, content):
    (OUT / name).write_text(content)

def phero(h1, lede, crumb, imgslot=None):
    inner = f'<p class="crumbs"><a href="index.html">Home</a><span aria-hidden="true">/</span><span>{crumb}</span></p><h1 class="display">{h1}</h1><p class="lede">{lede}</p>'
    if imgslot:
        return f'<section class="phero"><div class="wrap"><div>{inner}</div>{imgslot}</div></section><div class="band-strip pat-f" aria-hidden="true"></div>'
    return f'<section class="phero noimg"><div class="wrap"><div>{inner}</div></div></section><div class="band-strip pat-f" aria-hidden="true"></div>'

# ---------------- data ----------------
DISHES = [
 ('jollof', 'rice', 'Party Jollof Rice', 3500, 'Smoky party jollof cooked in a rich pepper base, served with fried plantain.', 'jollof', 'a'),
 ('fried-rice', 'rice', 'Native Fried Rice', 3800, 'Vegetable fried rice with prawns, sweet corn and a gentle hint of curry.', 'fried-rice', 'b'),
 ('egusi', 'soups', 'Egusi Soup & Pounded Yam', 4500, 'Melon seed soup simmered with assorted meat and stockfish, served with pounded yam.', 'egusi', 'c'),
 ('okra', 'soups', 'Seafood Okra Soup', 5200, 'Fresh okra with prawns, fish and periwinkle in a light palm oil base.', 'okra', 'd'),
 ('pounded-yam', 'soups', 'Pounded Yam', 1000, 'Smooth, freshly pounded yam, the perfect partner for any soup.', 'pounded-yam', 'e'),
 ('chicken', 'proteins', 'Peppered Chicken', 2800, 'Grilled chicken tossed in a fiery pepper glaze with onions and green pepper.', 'chicken', 'f'),
 ('asun', 'proteins', 'Asun (Peppered Goat Meat)', 4200, 'Smoked goat meat tossed with scotch bonnet, onions and a squeeze of lime.', 'asun', 'a'),
 ('coconut-rice', 'special', 'Coconut Rice & Grilled Fish', 6500, 'Fragrant coconut rice served with a whole grilled fish and fresh salad.', 'coconut-rice', 'b'),
 ('small-chops', 'snacks', 'Small Chops Platter', 5000, 'Puff puff, spring rolls, samosas, peppered gizzard and chicken skewers.', 'small-chops', 'c'),
 ('puff-puff', 'snacks', 'Puff Puff (10 pieces)', 1200, 'Golden, airy puff puff fried fresh to order.', 'puff-puff', 'd'),
 ('meat-pie', 'snacks', 'Meat Pie (2 pieces)', 1500, 'Flaky pastry filled with seasoned minced beef, potato and carrot.', 'meat-pie', 'e'),
 ('zobo', 'drinks', 'Chilled Zobo', 1200, 'House-brewed hibiscus drink with ginger, pineapple and a twist of lime.', 'zobo', 'f'),
]
CATS = [('all', 'All'), ('rice', 'Rice'), ('soups', 'Soups & swallow'), ('proteins', 'Proteins'), ('snacks', 'Small chops & snacks'), ('special', 'Special meals'), ('drinks', 'Drinks')]
CATLAB = {'rice': 'Rice dish', 'soups': 'Soup and swallow', 'proteins': 'Protein', 'snacks': 'Small chops and snacks', 'special': 'Special meal', 'drinks': 'Drink'}
naira = lambda n: '₦{:,}'.format(n)

def dish_card(d):
    id_, cat, name, price, desc, img, pat = d
    return f'''<article class="card dish" data-id="{id_}" data-cat="{cat}" data-name="{E(name)}" data-price="{price}" data-search="{E((name + ' ' + desc + ' ' + CATLAB[cat]).lower())}">
{slot(img, name, name + ', a Majikfingaz dish', 'r43', pat)}
<div class="card-body"><span class="kicker">{CATLAB[cat]}</span><h3>{E(name)}</h3><p>{E(desc)}</p>
<div class="card-foot"><span class="price">{naira(price)}</span><div class="ctl"></div></div></div></article>'''

# ---------------- HOME ----------------
def home():
    picks = [d for d in DISHES if d[0] in ('jollof', 'egusi', 'asun', 'small-chops')]
    pc = ''.join(f'''<article class="card dish">{slot(d[5], d[2], d[2] + ', a Majikfingaz dish', 'r43', d[6])}
<div class="card-body"><span class="kicker">{CATLAB[d[1]]}</span><h3>{E(d[2])}</h3><p>{E(d[4])}</p>
<div class="card-foot"><span class="price">{naira(d[3])}</span><button class="btn btn-plum btn-sm" type="button" data-quick data-id="{d[0]}" data-name="{E(d[2])}" data-price="{d[3]}" aria-label="Add {E(d[2])} to order">{ic('plus')}Add</button></div></div></article>''' for d in picks)
    marq = ['Party Jollof', 'Egusi & Pounded Yam', 'Asun', 'Small Chops', 'Puff Puff', 'Coconut Rice', 'Chilled Zobo', 'Red Velvet Cake', 'Meat Pie', 'Seafood Okra']
    mi = ''.join(f'<li>{m}</li>' for m in marq)
    h = head('Majikfingaz Food Villa | Nigerian Meals, Cakes and Catering in Apapa, Lagos',
             'Nigerian meals cooked daily, handcrafted cakes and event catering across Lagos. Order on WhatsApp from Majikfingaz Food Villa, 111 Oba Olu-Iwa Road, Olodi, Apapa.',
             '<script type="application/ld+json">{"@context":"https://schema.org","@type":"Restaurant","name":"Majikfingaz Food Villa","servesCuisine":"Nigerian","telephone":"+2348060020861","address":{"@type":"PostalAddress","streetAddress":"111 Oba Olu-Iwa Road, Olodi","addressLocality":"Apapa","addressRegion":"Lagos","addressCountry":"NG"},"openingHoursSpecification":[{"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],"opens":"09:00","closes":"21:00"},{"@type":"OpeningHoursSpecification","dayOfWeek":"Sunday","opens":"12:00","closes":"20:00"}],"sameAs":["https://www.instagram.com/majikfingaz_catering"]}</script>\n')
    b = header('index.html') + f'''
<section class="hero"><div class="wrap">
<div><span class="status" data-status role="status">{'<i></i>'}<span class="t">Checking hours</span></span>
<h1 class="display">Savor the tradition of Nigerian food</h1>
<p class="lede">Nigerian meals cooked daily, cakes made to order and celebration catering across Lagos. Order straight to our WhatsApp and we confirm within minutes.</p>
<div class="actions"><a class="btn btn-amber" href="menu.html" data-magnet>Order from the menu</a><a class="btn btn-ghost" href="catering.html" data-magnet>Plan your catering</a></div></div>
<div class="hero-art">{slot('hero-jollof', 'Hero photo: party jollof with plantain', 'Party jollof rice with fried plantain and grilled chicken', 'r11', 'a', eager=True)}
<div class="chip chip-1"><div>Party Jollof<small>Cooked fresh today</small></div><b>{naira(3500)}</b></div>
<div class="chip chip-2"><div>Red Velvet Cake<small>Ready in 48 hours</small></div><b>{naira(30000)}</b></div>
<div class="chip chip-3"><div>Puff Puff x10<small>Fried to order</small></div><b>{naira(1200)}</b></div></div>
</div></section>
<section class="facts" aria-label="Quick facts"><ul class="wrap">
<li>{ic('clock')}<div>Open six days and Sundays too<span>Mon to Sat 9am to 9pm, Sun 12pm to 8pm</span></div></li>
<li>{ic('truck')}<div>Catering Lagos-wide<span>Cooking, delivery, setup and service</span></div></li>
<li>{ic('cake')}<div>Cakes made to order<span>Best ordered 48 hours ahead</span></div></li></ul></section>
<div class="marquee" id="marquee" aria-label="Dishes we cook"><div class="marquee-track"><ul class="marquee-group">{mi}</ul><ul class="marquee-group" aria-hidden="true">{mi}</ul></div><button class="marquee-toggle" id="marqueeToggle" type="button" aria-pressed="false">Pause</button></div>

<section class="section"><div class="wrap">
<div class="sec-head"><h2 class="display">Three ways to enjoy Majikfingaz</h2><p>A table full of Nigerian favourites, a cake worth celebrating with, or a full catering service for the people you love.</p></div>
<div class="trio">
<a class="tile" href="menu.html">{slot('tile-meals', 'Nigerian meals photo', 'A spread of Nigerian meals', 'r43', 'b')}<div class="tbody"><span class="num">01</span><h3>Nigerian Meals</h3><p>Delicious Nigerian meals prepared with passion, flavour and quality ingredients.</p><span class="go">Explore our menu {ic('arrow')}</span></div></a>
<a class="tile" href="cakes.html">{slot('tile-cakes', 'Celebration cake photo', 'A celebration cake from Majikfingaz', 'r43', 'c')}<div class="tbody"><span class="num">02</span><h3>Cakes &amp; Pastries</h3><p>Beautifully crafted cakes and delightful pastries made to bring sweetness to every celebration.</p><span class="go">Build your cake {ic('arrow')}</span></div></a>
<a class="tile" href="catering.html">{slot('tile-catering', 'Catering table photo', 'A catering table set for an event', 'r43', 'd')}<div class="tbody"><span class="num">03</span><h3>Event Catering</h3><p>Professional food catering for weddings, celebrations, corporate functions and special occasions.</p><span class="go">Plan your event {ic('arrow')}</span></div></a>
</div></div></section>

<section class="section" style="background:var(--plum-tint)"><div class="wrap">
<div class="sec-head"><h2 class="display">Cooked fresh today</h2><p>A few favourites to start with. Add them to your order here or browse the full menu.</p></div>
<div class="cards">{pc}</div>
<p style="margin-top:32px"><a class="btn btn-line" href="menu.html">See the full menu {ic('arrow')}</a></p></div></section>

<section class="section how"><div class="wrap">
<div class="sec-head"><h2 class="display">Ordering takes four steps</h2><p>No accounts and no waiting on hold. Everything goes straight to our kitchen on WhatsApp.</p></div>
<ol><li><h3>Pick your dishes</h3><p>Browse the menu, search and add what you like.</p></li><li><h3>Check your order</h3><p>Change quantities and choose pickup or delivery.</p></li><li><h3>Send on WhatsApp</h3><p>Your order arrives as a ready-written message.</p></li><li><h3>We confirm</h3><p>We confirm within minutes and get cooking.</p></li></ol></div></section>

<section class="cta"><div class="wrap"><h2 class="display">Good food, beautiful moments and exceptional taste</h2>
<p>Visit us at 111 Oba Olu-Iwa Road, Olodi, Apapa, or send your order from wherever you are.</p>
<div class="actions"><a class="btn btn-amber" href="menu.html">Start your order</a><a class="btn btn-ghost" href="contact.html">Find us in Apapa</a></div></div></section>
''' + footer()
    write('index.html', h + b)

# ---------------- MENU ----------------
def menu():
    chips = ''.join(f'<button class="chipf" type="button" data-cat="{c}" data-label="{l}" aria-pressed="{"true" if c == "all" else "false"}">{l}</button>' for c, l in CATS)
    h = head('Menu | Majikfingaz Food Villa', 'Browse the Majikfingaz Food Villa menu: party jollof, egusi, asun, small chops and more. Add to your order and send it on WhatsApp.')
    b = header('menu.html') + phero('Cooked fresh every day', 'Search the menu, add what you fancy and send the order straight to our WhatsApp. We confirm within minutes.', 'Menu') + f'''
<div class="toolbar"><div class="wrap">
<div class="tb-row"><div class="search">{ic('search')}<input id="dishSearch" type="search" placeholder="Search jollof, goat, pie..." aria-label="Search the menu"></div>
<div class="sort"><label class="sr" for="dishSort" style="position:absolute;left:-999px">Sort dishes</label><select id="dishSort"><option value="default">Our order</option><option value="low">Price: low to high</option><option value="high">Price: high to low</option></select></div></div>
<div class="chips" role="group" aria-label="Filter by category">{chips}</div></div></div>
<section class="section" style="padding-top:36px"><div class="wrap">
<div class="result-meta"><span id="resultMeta" aria-live="polite"></span><span>Prices in naira</span></div>
<div class="cards" id="dishGrid">{''.join(dish_card(d) for d in DISHES)}</div>
<div class="empty" id="noResults" hidden><h3>Nothing matches that yet</h3><p>Try another word, or clear the filters to see the whole menu.</p><p style="margin-top:16px"><button class="btn btn-plum btn-sm" id="clearFilters" type="button">Clear filters</button></p></div>
<p class="menu-note">Cakes and catering orders are best placed 48 hours ahead. Looking for something not listed? Message us on WhatsApp and ask.</p>
</div></section>
''' + footer()
    write('menu.html', h + b)

# ---------------- CAKES ----------------
def cakes():
    h = head('Cakes & Pastries | Majikfingaz Food Villa', 'Build a custom celebration cake, order pastry trays or request a wedding cake from Majikfingaz Food Villa in Apapa, Lagos.')
    opts = lambda name, items, default: ''.join(
        f'<div class="opt"><input type="radio" id="{name}-{k}" name="{name}" value="{k}"{" checked" if k == default else ""}><label for="{name}-{k}"><b>{t}</b><span>{s}</span></label></div>' for k, t, s in items)
    sw = ''.join(f'<div class="sw"><input type="radio" id="f-{k}" name="frost" value="{k}"{" checked" if k == "plum" else ""}><label for="f-{k}"><i style="background:{c}"></i>{t}</label></div>' for k, t, c in
                 [('plum', 'Plum purple', '#6A1B86'), ('leaf', 'Leaf green', '#66A80F'), ('amber', 'Amber gold', '#E0902A'), ('cream', 'Cream white', '#FFF6E6')])
    cake = '''<svg viewBox="0 0 300 260" role="img" aria-label="Preview of your cake"><g id="cakeScale" transform="translate(150 215) scale(.92) translate(-150 -215)">
<ellipse cx="150" cy="222" rx="128" ry="12" fill="rgba(0,0,0,.28)"/>
<rect class="tier" x="40" y="150" width="220" height="72" rx="14" style="fill:#4A2A1A"/>
<path class="drip" d="M40 164c0-8 6-14 14-14h192c8 0 14 6 14 14v8c-10 0-10 14-20 14s-8-10-18-10-8 16-18 16-8-14-18-14-8 12-18 12-8-16-18-16-8 14-18 14-8-12-18-12-8 12-18 12-8-10-14-14z" style="fill:#6A1B86"/>
<rect class="tier" x="76" y="92" width="148" height="62" rx="12" style="fill:#6B3F2A"/>
<path class="drip" d="M76 104c0-7 5-12 12-12h124c7 0 12 5 12 12v6c-8 0-8 12-16 12s-7-9-15-9-7 13-15 13-7-11-15-11-7 10-15 10-7-12-15-12-7 9-15 9-6-8-7-12z" style="fill:#6A1B86"/>
<g id="fruit" style="display:none"><circle cx="110" cy="88" r="9" fill="#D8203C"/><circle cx="150" cy="84" r="9" fill="#D8203C"/><circle cx="190" cy="88" r="9" fill="#D8203C"/><circle cx="130" cy="82" r="6" fill="#66A80F"/><circle cx="170" cy="82" r="6" fill="#4A2A8A"/></g>
<g id="gold" style="display:none"><path d="M96 88l6-10 6 10-6 3zM142 84l8-12 8 12-8 4zM188 88l6-10 6 10-6 3z" fill="#E8B547"/><circle cx="82" cy="140" r="3" fill="#E8B547"/><circle cx="218" cy="132" r="3" fill="#E8B547"/><circle cx="150" cy="134" r="3" fill="#E8B547"/></g>
<rect x="100" y="166" width="100" height="26" rx="8" fill="#FFF6E6" opacity=".95"/><text id="plaqueTxt" x="150" y="184" text-anchor="middle" font-size="11" font-weight="700" fill="#2B0F38" font-family="Figtree,sans-serif">Congratulations</text>
</g></svg>'''
    items = [('choc', 'Signature Chocolate', 'Deep chocolate layers, silky ganache', 'Signature Chocolate Cake', 35000, 'cake-chocolate', 'Celebration cake', 'a'),
             ('straw', 'Strawberry Cream', '', 'Strawberry Cream Cake', 28000, 'cake-strawberry', 'Birthday cake', 'b'),
             ('red', 'Red Velvet Dream', '', 'Red Velvet Dream Cake', 30000, 'cake-redvelvet', 'Birthday cake', 'c')]
    ready = [
        ('cake-chocolate', 'Signature Chocolate Cake', 'Celebration cake', 'Deep chocolate layers with silky ganache and a whisper of gold.', 35000, 'a', 'chocolate-cake'),
        ('cake-strawberry', 'Strawberry Cream Cake', 'Birthday cake', 'Light sponge, fresh cream and strawberries, a birthday favourite.', 28000, 'b', 'strawberry-cake'),
        ('cake-redvelvet', 'Red Velvet Dream Cake', 'Birthday cake', 'Velvety cocoa sponge with cream cheese frosting and berry compote.', 30000, 'c', 'redvelvet-cake'),
        ('pie-tray', 'Meat Pie Tray (12 pieces)', 'Pastries', 'A party tray of our golden meat pies, baked fresh on the day.', 9000, 'd', 'pie-tray'),
        ('puff-pack', 'Puff Puff Party Pack', 'Pastries', 'Fifty pieces of warm puff puff, perfect for sharing.', 6000, 'e', 'puff-pack'),
    ]
    rc = ''.join(f'''<article class="card">{slot(s, n, n + ' from Majikfingaz', 'r43', p)}<div class="card-body"><span class="kicker">{k}</span><h3>{n}</h3><p>{d}</p>
<div class="card-foot"><span class="price">{naira(pr)}</span><button class="btn btn-plum btn-sm" type="button" data-quick data-id="{i}" data-name="{n}" data-price="{pr}" aria-label="Add {n} to order">{ic('plus')}Add</button></div></div></article>''' for s, n, k, d, pr, p, i in ready)
    rc += f'''<article class="card">{slot('cake-wedding', 'Gold Leaf Wedding Cake', 'Three-tier gold leaf wedding cake', 'r43', 'f')}<div class="card-body"><span class="kicker">Custom cake</span><h3>Gold Leaf Wedding Cake</h3><p>Three tiers of vanilla and red velvet finished with edible gold leaf. Made to your event, so we quote it together.</p>
<div class="card-foot"><span class="price">from {naira(180000)}</span><a class="btn btn-line btn-sm" target="_blank" rel="noopener" href="https://wa.me/2348060020861?text={'Hello%20Majikfingaz%20Food%20Villa%2C%20I%27d%20like%20a%20quote%20for%20a%20wedding%20cake.'}">Get a quote</a></div></div></article>'''
    b = header('cakes.html') + phero('Cakes made to celebrate', 'Design your cake below, add a message, and we will confirm the details and final price with you on WhatsApp. Best ordered 48 hours ahead.', 'Cakes &amp; pastries', slot('cakes-hero', 'Cakes hero photo', 'A Majikfingaz celebration cake', 'r11', 'c', eager=True)) + f'''
<section class="section cakes"><div class="wrap">
<div class="sec-head"><h2 class="display">Build your cake</h2><p>Pick a flavour, size and colour and watch it change. The price is an estimate until we confirm it with you.</p></div>
<form class="builder" id="builder" novalidate><div>
<div class="bstep"><h3><i>1</i>Flavour</h3><div class="opts">{opts('type', [('choc', 'Signature Chocolate', 'Ganache and a touch of gold'), ('straw', 'Strawberry Cream', 'Fresh cream and strawberries'), ('red', 'Red Velvet Dream', 'Cream cheese and berries')], 'choc')}</div></div>
<div class="bstep"><h3><i>2</i>Size</h3><div class="opts">{opts('size', [('s', 'Small', 'About 10 slices'), ('m', 'Standard', 'About 16 slices'), ('l', 'Large', 'About 25 slices'), ('x', 'Party', 'About 40 slices')], 'm')}</div></div>
<div class="bstep"><h3><i>3</i>Frosting colour</h3><div class="swatches">{sw}</div></div>
<div class="bstep"><h3><i>4</i>Finish</h3><div class="opts">{opts('fin', [('classic', 'Classic', 'Smooth buttercream'), ('fruit', 'Fresh fruit', 'Berries on top'), ('gold', 'Gold leaf', 'Edible gold, priced on confirmation')], 'classic')}</div></div>
<div class="bstep"><h3><i>5</i>Message and date</h3>
<div class="field" style="margin-top:0"><label for="cMsg">Message on the cake</label><input class="txt" id="cMsg" name="msg" maxlength="28" placeholder="Happy Birthday Ada" autocomplete="off"><div class="counter" id="msgCount" aria-hidden="true">0/28</div></div>
<div class="field"><label for="cDate">Date you need it</label><input class="txt" id="cDate" name="date" type="date"></div></div>
</div>
<aside class="preview" aria-label="Your cake summary"><div class="cake-art">{cake}</div>
<h3 id="pvName">Signature Chocolate Cake</h3>
<dl class="spec"><div><dt>Size</dt><dd id="pvSize"></dd></div><div><dt>Frosting</dt><dd id="pvFrost"></dd></div><div><dt>Finish</dt><dd id="pvFin"></dd></div><div><dt>Message</dt><dd id="pvMsg"></dd></div></dl>
<div class="price-row"><span>Estimated price</span><b id="pvPrice" aria-live="polite"></b></div>
<p class="fine">Estimate only. We confirm the final price, flavour details and delivery with you on WhatsApp.</p>
<button class="btn btn-amber" id="cAdd" type="button">{ic('plus')}Add to my order</button>
<button class="btn btn-ghost" id="cWa" type="button">{ic('chat')}Ask about this cake</button></aside></form></div></section>

<section class="section"><div class="wrap">
<div class="sec-head"><h2 class="display">Ready-to-order cakes and pastries</h2><p>Our favourites at their listed prices, plus party trays for sharing.</p></div>
<div class="cards cakes-grid">{rc}</div></div></section>
''' + footer()
    write('cakes.html', h + b)

# ---------------- CATERING ----------------
def catering():
    h = head('Event Catering in Lagos | Majikfingaz Food Villa', 'Wedding, birthday, corporate and private-dinner catering across Lagos by Majikfingaz Food Villa. Plan quantities and request a quote on WhatsApp.')
    chk = ''.join(f'<label><input type="checkbox" name="item" value="{v}"{" checked" if c else ""}><span>{t}<small>{s}</small></span></label>' for v, t, s, c in
                  [('jollof', 'Party jollof rice', 'The celebration classic', 1), ('fried', 'Native fried rice', 'With prawns and sweet corn', 0), ('soup', 'Soup and swallow', 'Egusi, okra and pounded yam', 0),
                   ('protein', 'Proteins', 'Chicken, asun or fish', 1), ('chops', 'Small chops', 'Puff puff, rolls, samosas, skewers', 1), ('drinks', 'Drinks', 'Zobo and more', 0)])
    pk = [('Intimate dinners', ['Nigerian classics with continental touches', 'Plated or buffet service', 'Ideal for private gatherings']),
          ('Weddings and celebrations', ['From a birthday to a 500-guest wedding', 'Cake and small chops can sit alongside the meal', 'We plan, cook and serve']),
          ('Corporate functions', ['Lunches, launches and staff events', 'Delivery and setup handled for you', 'Catering across Lagos'])]
    pkh = ''.join(f'<article><h3>{t}</h3><ul>{"".join(f"<li>{x}</li>" for x in l)}</ul></article>' for t, l in pk)
    b = header('catering.html') + phero('Let us cater your next celebration', 'From intimate dinners to weddings of several hundred guests, we plan, cook and serve food your guests will remember.', 'Catering', slot('catering-spread', 'Catering spread photo', 'A catering buffet of Nigerian dishes', 'r43', 'd', eager=True)) + f'''
<section class="section"><div class="wrap">
<div class="sec-head"><h2 class="display">Catering for every kind of gathering</h2><p>Tell us the occasion and we build a menu around it. Cooking, delivery, setup and service across Lagos.</p></div>
<div class="pkg">{pkh}</div></div></section>
<section class="catering"><div class="band pat-b" aria-hidden="true"></div>
<div class="wrap grid"><div><h2 class="display">How much food will you need?</h2>
<p class="lede">Slide to your guest count and choose what you would like to serve. You get a planning guide for quantities, then send it to us as a quote request.</p>
<ol class="steps"><li><div><h3>Tell us the occasion</h3><p>Wedding, birthday, corporate event or intimate dinner.</p></div></li><li><div><h3>Choose your menu</h3><p>Nigerian classics, continental touches and small chops.</p></div></li><li><div><h3>We handle the rest</h3><p>Cooking, delivery, setup and service across Lagos.</p></div></li></ol></div>
<form class="est-box" id="estimator" novalidate><h3 class="display" style="font-size:28px;color:var(--plum-deep);letter-spacing:-.015em">Catering planner</h3>
<div class="field"><label for="eEvent">Occasion</label><select id="eEvent" name="event" class="txt"><option>Wedding</option><option>Birthday</option><option>Corporate event</option><option>Intimate dinner</option><option>Other celebration</option></select></div>
<div class="field"><div class="range-row"><label for="eGuests" style="margin:0">Guests</label><b id="gVal">100</b></div><input id="eGuests" name="guests" type="range" min="10" max="500" step="5" value="100"></div>
<div class="field"><label>What would you like to serve?</label><div class="checks">{chk}</div></div>
<div class="out" id="estOut" aria-live="polite"></div>
<div class="row2"><div class="field"><label for="eDate">Event date</label><input id="eDate" name="date" type="date" class="txt"></div><div class="field"><label for="eArea">Venue or area</label><input id="eArea" name="area" class="txt" placeholder="Ikoyi, Lagos"></div></div>
<button class="btn btn-amber" type="submit">{ic('chat')}Request a quote on WhatsApp</button></form></div></section>
''' + footer()
    write('catering.html', h + b)

# ---------------- GALLERY ----------------
GAL = [
 ('jollof', 'food', 'Party jollof with plantain', 'r43', 'a'), ('cake-chocolate', 'cakes', 'Signature chocolate cake', 'r45', 'b'),
 ('event-wedding', 'events', 'A wedding table set for guests', 'r32', 'c'), ('asun', 'food', 'Smoky asun with onions and lime', 'r11', 'd'),
 ('small-chops', 'food', 'Small chops platter', 'r43', 'e'), ('cake-redvelvet', 'cakes', 'Red velvet dream cake', 'r11', 'f'),
 ('event-corporate', 'events', 'Corporate lunch service', 'r43', 'a'), ('egusi', 'food', 'Egusi soup and pounded yam', 'r45', 'b'),
 ('cake-wedding', 'cakes', 'Gold leaf wedding cake', 'r45', 'c'), ('puff-puff', 'food', 'Puff puff fried to order', 'r11', 'd'),
 ('kitchen', 'events', 'In the kitchen at Olodi', 'r32', 'e'), ('cake-strawberry', 'cakes', 'Strawberry cream cake', 'r43', 'f'),
 ('coconut-rice', 'food', 'Coconut rice with grilled fish', 'r43', 'a'), ('event-birthday', 'events', 'A birthday celebration spread', 'r11', 'b'),
]
def gallery():
    h = head('Gallery | Majikfingaz Food Villa', 'Plates, cakes and celebrations from Majikfingaz Food Villa, Apapa, Lagos.')
    chips = ''.join(f'<button class="chipf" type="button" data-cat="{c}" aria-pressed="{"true" if c == "all" else "false"}">{l}</button>' for c, l in [('all', 'All'), ('food', 'Food'), ('cakes', 'Cakes'), ('events', 'Events')])
    gi = ''.join(f'<button class="gi" type="button" data-cat="{c}" data-cap="{E(cap)}" aria-label="Open photo: {E(cap)}">{slot(s, cap, cap, r, p)}<span class="cap">{E(cap)}</span></button>' for s, c, cap, r, p in GAL)
    b = header('gallery.html') + phero('Plates, cakes and celebrations', 'A selection of the food we cook and the moments we cater for. Tap any photo to see it larger.', 'Gallery') + f'''
<section class="section" style="padding-top:36px"><div class="wrap">
<div class="chips" role="group" aria-label="Filter gallery" style="margin-bottom:28px">{chips}</div>
<div class="masonry" id="gallery">{gi}</div></div></section>
<div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="Photo viewer"><button class="lb-btn lb-close" id="lbClose" type="button" aria-label="Close photo">{ic('x')}</button>
<button class="lb-btn lb-prev" id="lbPrev" type="button" aria-label="Previous photo">{ic('left')}</button><button class="lb-btn lb-next" id="lbNext" type="button" aria-label="Next photo">{ic('right')}</button>
<div class="lb-in"><div class="ph r43 pat-a" id="lbSlot"></div><div class="lb-cap"><b id="lbCap"></b><span id="lbCount"></span></div></div></div>
''' + footer()
    write('gallery.html', h + b)

# ---------------- ABOUT ----------------
def about():
    h = head('About | Majikfingaz Food Villa', 'The story of Majikfingaz Food Villa: a home of Nigerian excellence in Olodi, Apapa, Lagos.')
    vals = [('01', 'Fresh ingredients', 'Produce and proteins sourced daily, never shortcuts.'), ('02', 'Cooked with passion', 'Recipes rooted in Nigerian kitchens, plated with care.'), ('03', 'Made for celebration', 'From a quiet lunch to a 500-guest wedding.')]
    vh = ''.join(f'<div class="val"><div class="num">{n}</div><h3>{t}</h3><p>{d}</p></div>' for n, t, d in vals)
    b = header('about.html') + phero('A home of Nigerian excellence', 'Great food brings people together. That belief is behind every meal, cake and catering table we prepare.', 'About us') + f'''
<section class="section"><div class="wrap split"><div><h2 class="display">Our story</h2>
<p>We are proud to be a home of Nigerian excellence. At Majikfingaz we believe great food brings people together, so we prepare every meal, cake and catering table with care, honouring the recipes of our kitchens while serving them with a modern touch.</p>
<p>Whether you are looking for a satisfying everyday meal or planning a memorable celebration, we are here to serve you with passion.</p>
<p style="margin-top:28px"><a class="btn btn-plum" href="contact.html">Visit the villa</a></p>
<div class="stats"><div><b data-count="7" data-suffix="">7</b><span>days a week, Sundays included</span></div><div><b data-count="3">3</b><span>specialties: meals, cakes, catering</span></div><div><b data-count="500" data-suffix="">500</b><span>guests and beyond at a wedding</span></div></div></div>
{slot('about-kitchen', 'Kitchen or chef photo', 'The Majikfingaz kitchen team at work', 'r45', 'b')}</div></section>
<section class="section" style="background:var(--plum-tint)"><div class="wrap"><div class="sec-head"><h2 class="display">What we stand for</h2><p>Three promises we keep in the kitchen, every day.</p></div><div class="values">{vh}</div></div></section>
<section class="cta"><div class="wrap"><h2 class="display">Taste it for yourself</h2><p>Order a meal today, or tell us about your next celebration.</p><div class="actions"><a class="btn btn-amber" href="menu.html">See the menu</a><a class="btn btn-ghost" href="catering.html">Plan catering</a></div></div></section>
''' + footer()
    write('about.html', h + b)

# ---------------- CONTACT ----------------
def contact():
    h = head('Contact & Location | Majikfingaz Food Villa', 'Find Majikfingaz Food Villa at 111 Oba Olu-Iwa Road, Olodi, Apapa, Lagos. Call or WhatsApp +234 806 002 0861.')
    faq = [('How do I place an order?', 'Add dishes to your order on the menu page and send it on WhatsApp. It arrives as a ready-written message and we confirm within minutes. You can also call us.'),
           ('When are you open?', 'Monday to Saturday 9am to 9pm, and Sunday 12pm to 8pm.'),
           ('How early should I order a cake or catering?', 'Cakes and catering orders are best placed 48 hours ahead. For large events, message us as early as you can.'),
           ('Do you cater outside Apapa?', 'Yes. Our catering covers Lagos, including cooking, delivery, setup and service.'),
           ('Do you deliver everyday meals?', 'Choose delivery when you send your order and we confirm the area and fee with you on WhatsApp.'),
           ('Where exactly are you?', '111 Oba Olu-Iwa Road (also 111 Kirikiri Road), near Wilmer Bus Stop, Olodi, Apapa, Lagos.')]
    fh = ''.join(f'<details><summary>{q}</summary><div class="ans">{a}</div></details>' for q, a in faq)
    maps = 'https://www.google.com/maps/search/?api=1&query=111+Oba+Olu-Iwa+Road+Olodi+Apapa+Lagos'
    b = header('contact.html') + phero('Find us in Apapa', 'Call, message us on WhatsApp or come and eat. We would love to hear from you.', 'Contact') + f'''
<section class="section"><div class="wrap contact-grid">
<form class="cform" id="contactForm" novalidate><h2>Send us a message</h2><p class="help" style="color:var(--muted)">It opens WhatsApp with your message ready to send.</p>
<div class="field"><label for="cName">Your name</label><input class="txt" id="cName" name="name" autocomplete="name" required aria-describedby="eName"><div class="err" id="eName" role="alert"></div></div>
<div class="row2"><div class="field"><label for="cPhone">Phone (optional)</label><input class="txt" id="cPhone" name="phone" type="tel" autocomplete="tel"></div>
<div class="field"><label for="cTopic">Topic</label><select class="txt" id="cTopic" name="topic"><option>Order or menu question</option><option>Cake enquiry</option><option>Catering enquiry</option><option>Something else</option></select></div></div>
<div class="field"><label for="cMessage">Message</label><textarea id="cMessage" name="message" required aria-describedby="eMsg"></textarea><div class="err" id="eMsg" role="alert"></div></div>
<button class="btn btn-amber" type="submit">{ic('chat')}Send on WhatsApp</button></form>
<div><div class="mapcard"><div class="pat pat-b" aria-hidden="true"><div class="pin"><svg viewBox="0 0 24 24"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3" fill="#2B0F38"/></svg></div></div>
<div class="mb"><h3>Majikfingaz Food Villa</h3><p>111 Oba Olu-Iwa Road, near Wilmer Bus Stop, Olodi, Apapa, Lagos.</p>
<div class="btns"><a class="btn btn-amber btn-sm" href="{maps}" target="_blank" rel="noopener">{ic('pin')}Open in maps</a><a class="btn btn-ghost btn-sm" href="tel:+2348060020861">{ic('phone')}Call</a><a class="btn btn-ghost btn-sm" href="tel:+2349053622980">Call second line</a></div></div></div>
<div class="panel" style="margin-top:24px"><div class="ico">{ic('clock')}</div><h3>Opening hours</h3>
<span class="status" data-status role="status" style="background:var(--leaf-tint);color:var(--plum-deep);align-self:flex-start"><i></i><span class="t">Checking hours</span></span>
<dl class="hours"><div data-days="1,2,3,4,5,6"><dt>Monday to Saturday</dt><dd>9:00am to 9:00pm</dd></div><div data-days="0"><dt>Sunday</dt><dd>12:00pm to 8:00pm</dd></div></dl>
<p class="muted">Cakes and catering orders are best placed 48 hours ahead.</p></div></div></div></section>
<section class="section" style="background:var(--plum-tint)"><div class="wrap"><div class="sec-head"><h2 class="display">Questions, answered</h2><p>Quick answers before you message. Not here? Just ask us.</p></div><div class="faq">{fh}</div></div></section>
''' + footer()
    write('contact.html', h + b)


# ---------------- 404 ----------------
def notfound():
    h = head('Page not found | Majikfingaz Food Villa', 'The page you are looking for could not be found.')
    b = header('') + phero('We could not find that page', 'The link may be old or mistyped. Here are some good places to go next.', 'Not found') + f'''
<section class="section"><div class="wrap" style="display:flex;gap:12px;flex-wrap:wrap">
<a class="btn btn-plum" href="index.html">Back to home</a><a class="btn btn-line" href="menu.html">See the menu</a><a class="btn btn-line" href="contact.html">Contact us</a></div></section>
''' + footer()
    page = h + b
    # 404.html is served from any path, so make every local URL root-relative
    for a in ('assets/',):
        page = page.replace('href="' + a, 'href="/' + a).replace('src="' + a, 'src="/' + a)
    for n in ('index', 'menu', 'cakes', 'catering', 'gallery', 'about', 'contact'):
        page = page.replace(f'href="{n}.html"', 'href="/"' if n == 'index' else f'href="/{n}"')
    write('404.html', page)

# ---------------- build ----------------
def build():
    css = (HERE / 'base.css').read_text() + (HERE / 'extra.css').read_text()
    (OUT / 'assets/site.css').write_text(css)
    shutil.copy(HERE / 'site.js', OUT / 'assets/site.js')
    for f in (home, menu, cakes, catering, gallery, about, contact, notfound):
        f()
    # image checklist
    lines = ['# Image slots', '', 'Drop each photo into `assets/img/` using the exact filename below (`.webp`, `.jpg`, `.png` or `.avif`). Until a file exists the page shows a branded placeholder. Landscape 4:3 unless noted.', '',
             '| Filename | What it shows | Shape |', '|---|---|---|']
    for k, (lab, ratio) in SLOTS.items():
        lines.append(f'| `{k}` | {lab} | {ratio.replace("r43", "4:3").replace("r11", "square").replace("r45", "4:5 portrait").replace("r32", "3:2")} |')
    (R / 'docs' / 'IMAGES.md').write_text('\n'.join(lines) + '\n')
    print(len(SLOTS), 'slots')
build()
