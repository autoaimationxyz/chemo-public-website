# Design restoration and content review — 24 November 2026

**Design = 7ba7c25 layout; content = final profile including PAN, banking and audit details.** The final profile is dated 12 November 2026. Its wording is integrated into the website design; its PDF page structure is not copied.

## Exact content changes against 7ba7c25

| Page | Added or corrected content | Profile pages |
| --- | --- | --- |
| About — company information | PAN No. and common-for-all-offices note | 3 |
| About — Banking & Audit | Both bank names/branches, account numbers, IFSCs and the auditor; styled with the existing company-facts block | 3 |
| About — approach | Full five company-background paragraphs replace shortened paraphrases inside the original two-column section | 7 |
| About — mission | Exact introduction and all five commitments replace the abbreviated sentence | 6 |
| About — values | Add the values introduction; normalize the Passion apostrophe to the source wording; keep all six existing values/cards | 6 |
| About — quality policy | Add the profile's Partner sign-off; existing policy, three commitments and responsibility statement already match | 5 |
| About — team | Restore the four key biographies verbatim, including A/Graduate wording, years of experience, equipment examples, 14 years' sales experience and water/steam project wording. Keep the same people, roles and card layout | 8 |
| Certifications | Add PAN and its registration date in the existing Tax & Business Registrations table; include PAN in the page description | 4 |
| Solutions — delivery | Add How We Work (team/design/execution/repeat orders), quality/safety statements, the execution introduction and six steps, and all five Why Work With Us statements inside the existing delivery section | 9–10 |

## Compared and already correct

| Profile section | Website | Result |
| --- | --- | --- |
| Establishment, countries, counts and capabilities | Home and supporting pages | No factual correction needed; original hero and animated model restored |
| Offices, phones, emails, GST and partners | Contact, About, footer | No correction needed |
| Licences/contractor/business registrations | Certifications | No correction beyond the PAN/date row |
| Vision | About | Existing wording matches |
| Support team, qualifications and experience | About | All four support-team cards already match |
| Industries | Projects | All 23 sectors and 20+ aggregate retained |
| Product range | Products | All 56 scopes/main makes already match; catalogue layout, guidance, imagery and controls restored |
| Solution captions and makes | Solutions/product dialogs | All 36 approved entries already match |
| OEM partners | Solutions | 40+ claim and approved names already correct, including Bronx Systems, Recons, KSB and Phoenix Contact |
| Clients/projects | Projects | Approved names, locations, capacities, Satya Sai and Umang's ongoing DMRC Phase-IV wording already correct; complete original layout restored |

## Design verification

All CSS, JavaScript, images and the animated system diagram are restored byte-for-byte from 7ba7c25. A baseline hash manifest protects them. Home, Products, Projects, Contact, Quote and the legacy redirect regenerate byte-for-byte as at that commit. Only About, Solutions and Certifications receive the content additions above. No original page section, image or interactive element is removed.

PDF cover/index pages, numbered PDF section labels and literal letter-spaced headings are absent from rendered pages. The source checker rejects their return. The normalized source reference may retain document headings as evidence, but they are not rendered as website sections.

## Validation

Run build.py, content-check.py, browser-check.cjs, journey-check.cjs and accessibility-check.cjs. The original browser journeys, system focus/pause, imagery, six viewport sizes, catalogue/deep links, mobile menu, enquiry persistence, reduced motion and copy fallback are retained. Screenshots are captured for Home, About and Projects at 390px and 1440px outside the public repository. Automated accessibility checks do not replace physical-device or complete assistive-technology review.

Publication is an ordinary new commit pushed to main and gh-pages together, without git revert or force-push. The PDF itself is not uploaded. Schoolerp, unrelated repositories and Drive remain unchanged.