# Chemotech International website

Static HTML, CSS and JavaScript. The only factual authority is **Chemotech International - Company Profile (Final, Nov 2026).pdf**, dated 12 November 2026.

The confidential original PDF is not included or linked for download. `tools/approved-profile-public.txt` contains the public reference text with banking, audit and PAN details removed. Do not add bank details, KYC documents, prices or confidential lists.

## Editing and content rules

- `tools/company.json`: approved company information, industries, OEM names, contacts and projects.
- `tools/products.json`: exactly 56 final-profile families, scopes and main makes. `catalogue_no` is the PDF's printed order; `no` preserves existing links and saved enquiries.
- `tools/solutions.json`: the 36 final-profile solution captions, makes and image associations.
- `tools/build.py`: page templates, approved team/registration/policy copy and metadata.
- `assets/js/`: catalogue, accessible navigation and enquiry drafts.

The PDF supports the aggregate **300+ variants**, but does not enumerate 332 individual variants. Individual variant rows and master-list-only specifications are excluded. Main makes on product pages and solution-specific makes follow their respective PDF sections. Representative photographs retain source/licence credits and are not presented as completed-project photographs.

Do not import a product master or older profile into this public build. The legacy import utilities are historical tools, not approved publishing inputs. New factual edits must be reconciled against the final PDF and its sanitized reference before publishing.

```sh
python tools/build.py .
python tools/content-check.py
python -m http.server 8080
```

Run browser checks with Playwright installed outside the checkout and Chromium available:

```sh
node tools/browser-check.cjs
node tools/journey-check.cjs
node tools/accessibility-check.cjs
```

`SITE_URL` can override the test server. Checks cover eight pages at 320, 390, 768, 1024, 1440 and 1920px, filters, dialogs, legacy links, mobile menus, reduced motion, draft validation, clipboard fallback, saved selections and cross-tab updates. Safari and physical-device testing remain separate checks.

Private checks read one regular expression per line from the ignored `tools/private-patterns.txt`. Blank lines and lines starting with `#` are ignored. Keep confidential patterns only in that local file. When it is absent, the check prints a warning and runs all remaining checks.

## Enquiries

A floating WhatsApp link is available on every page, with a Call button on mobile. Contact and quote forms still prepare email drafts; they do not send enquiries to a server. Visitors must send the draft in their email service. Copying has a selectable-text fallback. Product selections stay in the visitor's browser. No email delivery or backend receipt is claimed.

## Deployment

`main` is the source branch; `gh-pages` is the deployment branch. Build and run checks before pushing. When their histories permit, publish the verified commit to both with:

```sh
git push --atomic origin HEAD:main HEAD:gh-pages
```

If the branches have diverged, reconcile their changes first; do not force-push. `.nojekyll` serves the static files directly. Canonicals, structured data, robots and sitemap use `https://autoaimationxyz.github.io/chemo-public-website/`. Update these together if a custom domain is introduced.

This repository and deployment do not replace or modify `web.schoolerp.org/chemotech-international/`.
