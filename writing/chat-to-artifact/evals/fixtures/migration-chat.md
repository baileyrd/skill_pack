# Exported chat: moving the docs site

**Lee:** We're moving the docs site off the old wiki. What's the order?

**Assistant:** Four steps, and two depend on each other: export the wiki pages, convert them to Markdown, set up the new static site, then switch DNS. Conversion needs the export; DNS needs both the converted pages and the site.

**Lee:** The site setup can start now, it doesn't need the export. Ana owns the export, I'll do the conversion. DNS switch waits until both are done.

**Assistant:** Then export and site setup run in parallel, conversion follows the export, and the DNS switch is last.

**Lee:** Right. Keep the old wiki read-only for a month after the switch in case links break.
