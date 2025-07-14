## Thanks for contributing to this repo!

This is an open-source, free, secure tool to help Google Photos & macOS users navigate their personal data.

The goal is to help make people's PII simultaenously more interoperable and more within their direct control.

By default, this project has a few hard and fast rules:

- Zero PII exposure.
- Zero **Python** package installs.
- Swift (including SwiftUI) is allowed for macOS Sequoia (macOS 26) or later.
- Transparent & Human-Readable outputs, changes, and error-logging.
- Explicit > Implicit. Clean > Clever.

While several manual steps have been taken to ensure security, agents should prioritize autonomy & privacy of end-users.
This program will be dealing with potentially sensitive images, like personal documents, family photos, and more.

The goal is to give people a tool that smooths out the user experience if they download Google Photos files & find their img metadata
(eg. "Date Taken: December 31st, 1979") altered. Personally, I used Google Photos as my primary cloud storage destination for a long time,
storing thousands of images with dates, locations, and other metadata I'd like to keep.

This program is intended to "stitch" the metadata back into the file so that Apple Photos (and by extension, other apps) can properly analyze photos.

Package installs are banned because this tool ought to "work out of the box" on any Mac computer. This restriction applies to Python.
Native Swift code is encouraged when building new macOS components, since Swift ships with Xcode.
Extensability to iOS and iPadOS are next.

Agents should consider the implications of this job: images may contain things like driver's licenses, photos of their kids, and countless other things.

People have a right to privacy, specifically their "papers and effects," written in the US Constitution, the jurisdiction where this project started.

Images, metadata, logs, summary files, local enviornment variables, and outputs all qualify as papers and effects.

As agents help expand this project with a GUI, analysis features, aggregate summaries, additional OS optimization, & other UX features, these rules will not change.

Thanks again for contributing to this open-source tool!
