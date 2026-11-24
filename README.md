# Chemotech International website

The website matches **Chemotech International - Company Profile (Final, Nov 2026).pdf**, dated 12 November 2026, exactly. **BANK DETAILS: INCLUDE**, by the owner's decision on 24 November 2026. PAN, its registration date, auditor information and both banking entries are required profile content. Do not apply the earlier omission rule.

Navigation, enquiry forms, WhatsApp/Call links, image credits and legal footer text are the only non-profile content exceptions. The original PDF is not uploaded or linked for download. The existing schoolerp site is untouched.

## Source and page mapping

`tools/approved-profile-public.txt` contains the complete extracted profile text. `tools/company.json` holds the page-by-page approved text and structured company information, including the bank decision. `tools/products.json` has exactly the 56 product families, their printed scopes and main makes; individual master-list variant rows remain excluded because the final PDF does not enumerate them. `tools/solutions.json` has the 36 final-profile image captions and makes.

| Profile pages | Website |
| --- | --- |
| 1–2, cover, index and at a glance | Home |
| 3, key information, offices, PAN, banking and audit | About — Key Information |
| 4, licences and registrations, including PAN/date | Licences & Registrations |
| 5–10, quality, mission/values, background, team and execution | About |
| 11, industries served | Projects — Our Presence |
| 12–15, product families and main makes | Products |
| 16–22, solutions and OEM partners | Solutions |
| 23, clients and projects | Projects |

Contact repeats the approved office details alongside the enquiry form. Product IDs, saved enquiries and legacy redirects stay compatible. Only solution photos from the final profile are shown; the old conceptual engineering scene and extra representative product imagery are removed. Source sections are complete rather than shortened marketing summaries.

Edit sources and run `python tools/build.py .`; generated HTML must match a clean rebuild. The content check verifies complete source sections, product/make evidence, required registration/banking/audit items, local links, metadata and reproducible output. It no longer bans approved profile fields.

## Before every push

Start `python -m http.server 8080` in another terminal. Playwright, Chromium and axe-core are test dependencies installed outside this static checkout.

```sh
python tools/build.py .
python tools/content-check.py --require-private
node tools/browser-check.cjs
node tools/journey-check.cjs
node tools/accessibility-check.cjs
```

Stop if a check fails. Then commit only the intended public files and publish the same commit to both branches:

```sh
git push --atomic origin HEAD:main HEAD:gh-pages
```

Do not force-push. `main` is the source and `gh-pages` is the deployment. GitHub Actions runs the content check without `--require-private`, as it has no local pattern file.

`tools/private-patterns.txt` stays local and ignored. With BANK DETAILS set to INCLUDE, it has no active bans on final-profile content. Its status is PASSED with zero patterns; the mandatory profile-content checks still run. `--require-private` fails if the local file is missing. Do not put unrelated private identifiers or credentials in the repository. If the owner later changes the bank decision to EXCLUDE, update the approved public data and add only bank exclusions to that local file before rebuilding.

## Enquiries

Email forms prepare drafts; visitors must send them from their email service. Copying has a selectable fallback. WhatsApp opens a prefilled message and Call is shown on mobile. No external scripts, automatic message sending or form backend are added.

## Website status – 24 Nov 2026

The public-content rule now includes every final-profile section, including PAN, audit and banking. Earlier statements that those fields were omitted are superseded. The sanitized root history is followed by ordinary maintenance commits. Custom domain and visitor analytics remain undecided.

Praneel can still recheck the old commit URL on 25 November and contact GitHub Support about cached history if needed; this relates to superseded master-list material, not the currently approved profile content. No further history rewrite is part of this update.

This repository and deployment do not replace or modify `web.schoolerp.org/chemotech-international/`.