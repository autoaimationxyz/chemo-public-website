# Chemotech International website

**Design = 7ba7c25 layout; content = final profile including PAN, banking and audit details.** The authoritative content source is the final company profile dated 12 November 2026. The profile supplies facts and wording, not the website's structure.

Keep the approved home hero, animated system diagram, imagery, catalogue and guidance, project/solution layouts, navigation and WhatsApp/mobile Call controls. Do not replace them with PDF cover pages, section-number labels, a PDF index or literal letter-spaced headings. The PDF itself is not uploaded or offered for download.

## Sources

- `tools/build.py`: approved page templates with profile-backed content additions.
- `tools/company.json`: company, offices, contacts, projects, PAN, banking/audit and exact approved copy for company background, mission, biographies and execution.
- `tools/products.json`: 56 families, approved scopes and main makes. Do not import extra master-list variant rows.
- `tools/solutions.json`: 36 approved solution captions and make associations.
- `tools/approved-profile-public.txt`: normalized reference text from the final profile, including the owner-approved financial and audit information.
- `tools/design-baseline.json`: hashes of every original design asset and the system diagram from 7ba7c25. The check rejects changed or missing assets.

## Content changes within the restored design

About adds PAN/common-office wording to company facts and a Banking & Audit block using the existing company-facts styling. It restores full company-background paragraphs, the mission introduction and five commitments, values introduction, policy sign-off and complete biographies for the four key people. The four support-team cards, names, roles, qualifications and experience figures remain correct.

Certifications adds the PAN/date row to the existing registrations table. Solutions keeps its four disciplines, galleries and delivery chain, and adds the final profile's How We Work, six execution steps and five Why Work With Us statements inside the existing delivery section, using its existing disclosure/list styles.

Home, Products, Projects, Contact and Quote retain the approved page content and structure. Product makes, solution captions, OEM names, client names, project wording, counts, licences and contact details were compared with the final profile and did not need further corrections. See LAUNCH-REVIEW.md for the page-by-page review.

## Before every push

Start `python -m http.server 8080` in another terminal. Playwright, Chromium and axe-core are installed outside the checkout.

```sh
python tools/build.py .
python tools/content-check.py --require-private
node tools/browser-check.cjs
node tools/journey-check.cjs
node tools/accessibility-check.cjs
```

The content check requires the PAN/date, banking and auditor facts, validates approved copy, checks unchanged design assets, rejects PDF section/index layouts and literal letter spacing, and verifies links, metadata and reproducible HTML. Browser checks retain the original system-diagram focus/pause, catalogue, mobile, form and enquiry journeys. Do not remove a check simply to make a different design pass.

Stop on any failure. Commit only intended public files, then publish one commit to both branches:

```sh
git push --atomic origin HEAD:main HEAD:gh-pages
```

No force-push or history revert is used. GitHub Actions runs without `--require-private` because it does not have the ignored local file. `tools/private-patterns.txt` has no active bans on the owner-approved PAN/banking/audit content. It remains local and must never be committed.

## Enquiries and hosting

The existing forms prepare email drafts; visitors must send them in their own email service. Copying has a selectable fallback. WhatsApp opens a prefilled message, and Call appears on mobile. No third-party scripts or automatic sending are added.

`main` is source; `gh-pages` is deployment. Canonicals, robots, sitemap and metadata use the GitHub Pages address. Custom domain and visitor analytics remain undecided. Praneel can recheck the old cached commit URL on 25 November and contact GitHub Support if superseded master-list history remains accessible.

The existing `web.schoolerp.org/chemotech-international/` site, unrelated repositories and Google Drive remain untouched.