# Majikfingaz Food Villa: website

Restaurant, cakes and catering website for Majikfingaz Food Villa, Apapa, Lagos.
Built by Vicks Creative Studios.

## What this project is

A **plain static website: HTML, CSS and vanilla JavaScript.** There is no React, Vite or other framework, and **no build step is needed to deploy**. Everything in `public/` is the finished site.

- Animations: GSAP 3 and ScrollTrigger (included locally in `public/assets/`)
- Fonts: Bricolage Grotesque and Figtree, self-hosted (`public/assets/fonts/`), so no Google Fonts request is made
- Images: 29 photos plus logos in `public/assets/img/` (WebP)
- Pages: Home, Menu, Cakes, Catering, Gallery, About, Contact, plus a 404 page

## Folder layout

```
public/            <- the site. This is what Cloudflare Pages publishes
  *.html           pages
  assets/          site.css, site.js, gsap, fonts, img/
  _headers         security + cache headers (Cloudflare reads this)
  robots.txt
  404.html         shown automatically for unknown URLs
source/            optional: generator and source CSS/JS (see "Editing")
docs/IMAGES.md     list of the image file names
wrangler.toml      optional, only for command-line deploys
package.json       optional helper scripts
```

## Deploy on Cloudflare Pages (from GitHub)

1. Create a new GitHub repository and upload everything in this folder (keep the `public` folder as it is).
2. In Cloudflare, go to **Workers & Pages > Create > Pages > Connect to Git** and choose the repository.
3. Use these build settings:
   - **Framework preset:** None
   - **Build command:** leave empty
   - **Build output directory:** `public`
4. Click **Save and Deploy**. The site goes live at `https://<project-name>.pages.dev`.
5. To use your own domain: Pages project > **Custom domains > Set up a domain**.

Every later push to GitHub redeploys automatically.

### Alternative: direct upload (no GitHub)
Pages > Create > **Upload assets**, then drag the `public` folder in. Or from a terminal: `npx wrangler pages deploy public --project-name majikfingaz-food-villa`.

## Check it locally
`npx serve public` (or `python3 -m http.server -d public 8000`), then open the address shown.

## URLs
Links between pages use files such as `menu.html`. Cloudflare Pages also serves them without the extension (`/menu`), so both forms work.

## Editing

- **Swap a photo:** replace the file in `public/assets/img/` with the same name (see `docs/IMAGES.md`). WebP, JPG or PNG with the same base name all work.
- **Change text, prices, menu items:** these live in `source/gen.py`. Edit it, then run `python3 source/gen.py` (Python 3 only, no packages) to rebuild `public/`. You can also edit the HTML in `public/` directly for quick text fixes.
- **Styles and behaviour:** `source/base.css`, `source/extra.css`, `source/site.js` (rebuilt into `public/assets/` by the same command).

## Backend services and integrations

**There is no backend, database, API key or environment variable.** Nothing needs configuring on Cloudflare beyond the steps above. The site relies on these external destinations, all plain links:

| What | Where | Used for |
|---|---|---|
| WhatsApp | `wa.me/2348060020861` | Cart/order drawer, cake builder, catering planner and contact form all open WhatsApp with a ready-written message. No server stores orders |
| Phone | `tel:+2348060020861`, `tel:+2349053622980` | Call buttons |
| Instagram | `instagram.com/majikfingaz_catering` | Footer link |
| Google Maps | search link on Contact page | Directions |

Other details:
- The cart is remembered in the visitor's browser (localStorage key `mfv-cart`). Nothing is sent anywhere.
- "Open now" status uses Lagos time (Mon to Sat 9am to 9pm, Sun 12pm to 8pm).
- Forms do not email anyone: they hand the message to WhatsApp. If you later want orders by email or a database, that needs a separate service (for example Cloudflare Pages Functions or a form provider).
- `_headers` sets a strict Content-Security-Policy that allows only this site's own files. If you later add third-party scripts (analytics, chat widgets, embedded maps), add their domains to that policy.

## To confirm before launch
- The photos are AI-generated food images; replace them with real photos of your dishes when you have them.
- Cake size multipliers, catering quantity guidance and delivery wording are working assumptions. Check them against your real pricing.
