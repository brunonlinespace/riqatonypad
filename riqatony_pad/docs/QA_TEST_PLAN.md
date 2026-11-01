## 2.0.0-x13.2 — Message feedback parity

Verify each new message appears in the editor's existing left status-message field after successful Open, Save (including unchanged-file Save), Save As, Rename, external-editor launch and containing-folder launch; on empty Paste as Plain Text; and on either Insert/Overwrite transition. Cancellations, launch failures, invalid files and failed writes must not emit success feedback. An RTF compatibility warning must not be displaced by an ordinary Loaded confirmation. Protected Save Version As must retain its preservation-specific feedback without a generic Save As precursor. The right permanent indicator must remain intact and no window geometry or styling must change. Run `qa/static-qa.sh` and live Fedora KDE/Wayland validation.

# Ricopad 1.0.15 QA test plan

Ricopad 1.0.15 retains the 1.0.12 behavioral baseline and changes only approved UI wording/tooltips and Quick Tour footer placement.

Release gates verify:
- Ribbon/Retro command icons use 36×36 within unchanged 52×52 controls.
- Help action is `Quick Tour…`.
- startup no longer marks the tour suppressed merely because it was shown; the checkbox controls the persisted preference.
- the first page uses QWizard `NoBackButtonOnStartPage`.
- all seven existing Quick Tour page titles/body strings remain byte-for-byte equivalent as strings.
- package metadata/builders identify Ricopad 1.0.15.
- critical RTF/support/lifecycle behavior remains unchanged.
- Clear Colour and workspace/setup-wizard work remain outside scope.
