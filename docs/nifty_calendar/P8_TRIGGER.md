# P8 Trigger

Branch: `research-nifty-4leg-calendar-p8-oos-validation`

Workflow:
`.github/workflows/p8-nifty-oos-validation.yml`

The workflow has both:
- push trigger for the P8 source files;
- manual `workflow_dispatch`.

No P8 result is accepted from an uncommitted or locally modified input set.
