# calibre-rename

First, install dependency.

```bash
poetry install --no-dev
```

Then you are ready to go.

```bash
$ poetry run calibre-rename --help

Usage: calibre-rename [OPTIONS] [PATHS]...

Options:
  -p, --author-prefix TEXT  Prefix for author(s). Default: " - ".
  -e, --epub                Also rename `.epub`.
  -k, --kepub               Also rename `.kepub` and `.kepub.epub`.
  -z, --zipfile             Also rename `.zip` and `.cbz`.
  -o, --opf                 Also rename `metadata.opf`.
  -g, --get-cover           Get cover image from Amazon.
  --help                    Show this message and exit.
```

## Description

When you add a book to [Calibre](https://calibre-ebook.com/),
it will automatically change the filename to one that uses only ASCII characters.

If the original filename uses non-alphanumeric characters, such as CJK,
Calibre renames the file to ASCII based on the pronunciation of the string.

However, the reading of the original language is not accurate,
and the converted file name is often unintelligible as a result.

This script reads metadata from azw3 files and reverts their filenames
to the original language (like Japanese).

If there are epub, kepub, or zip format files with the same basename
(just different extensions), you can rename them simultaneously.

A book title may be truncated to keep the filename (including ASIN, authors,
and extension) under appx. 240bytes (to prevent OSError).

Note that Calibre insists on its way of naming files. So files renamed with
this script are no longer under control by Calibre. However, you can always
add them back to the app (and manage them again with gibberish filenames)
if you want to.

