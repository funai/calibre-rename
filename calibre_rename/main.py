#!/usr/bin/env python3

import click
from ebookatty import get_metadata
import os
import subprocess
import re
import shutil
import urllib.request

@click.command()
@click.option('-p', '--author-prefix', 'prefix',
		default=' - ', help = 'Prefix for author(s). Default: " - ".')
@click.option('-e', '--epub', 'epub',
		is_flag=True, help = 'Also rename `.epub`.')
@click.option('-k', '--kepub', 'kepub',
		is_flag=True, help = 'Also rename `.kepub` and `.kepub.epub`.')
@click.option('-z', '--zipfile', 'zipfile',
		is_flag=True, help = 'Also rename `.zip` and `.cbz`.')
@click.option('-o', '--opf', 'opf',
		is_flag=True, help = 'Also rename `metadata.opf`.')
@click.option('-g', '--get-cover', 'getcover',
		is_flag=True, help = 'Get cover image from Amazon.')
@click.argument('paths', type=click.Path(exists=True), nargs=-1)
def main(paths, prefix, epub, kepub, zipfile, opf, getcover):
	for infile in paths:
		if not infile.endswith('.azw3'):
			continue
		meta = get_metadata(infile)
		meta['Title'] = meta['updatedtitle'][0]
		author = []
		for x in meta['author']:
			x = x.strip()
			if re.match(r'^\w+,\s*\w+', x):
				last, first = x.split(',', 1)
				author.append(' '.join([first.strip(), last.strip()]))
			else:
				author.append(x.strip())
		meta['Author(s)'] = ', '.join(author)
		title = (sanitize(meta['Title']))
		author = sanitize(meta['Author(s)'], nobracket=True).title()
		asin = meta['asin'][0]
		# ext4 allows max 255bytes for filename.
		suffix_bytes = len(('.' + asin + prefix + author + '.kepub.epub').encode()) + 21 # to prevent OSError in Kepubify.
		_MAX_WIDTH = 255
		byte_width = _MAX_WIDTH - suffix_bytes
		title = shorten_to_bytes_width(title, byte_width)
		newname = title + '.' + asin + prefix + author
		print('# ' + newname)
		path, filename = os.path.split(os.path.abspath(infile))
		# removesuffix @Python ^3.9
		basename = filename.removesuffix('.azw3')
		rename_book(path, basename, newname, '.azw3')
		if zipfile:
			rename_book(path, basename, newname, '.zip')
			rename_book(path, basename, newname, '.cbz')
		if kepub:
			rename_book(path, basename, newname, '.kepub')
			rename_book(path, basename, newname, '.kepub.epub')
		if epub:
			rename_book(path, basename, newname, '.epub')
		if getcover:
			get_cover(path, newname, asin)
		if opf:
			rename_opf(path, newname)

def sanitize(str, nobracket=False):
	if nobracket:
		str = re.sub(r'\[[^\]]*\]', '', str)
	str = re.sub(r'[:/\\{}]', '_', str)
	str = re.sub('__+', '_', str)
	str = re.sub('^_|_$', '', str)
	return str.strip()

def rename_book(dirname, base, new, ext):
	base_path = os.path.join(dirname, base + ext)
	new_path = os.path.join(dirname, new + ext)
	if os.path.exists(base_path):
		if os.path.exists(new_path):
			print(f'Already renamed: {new}{ext}')
		else:
			os.rename(base_path, new_path)
	else:
		print('Not found: {}'.format(base_path))

def rename_opf(dirname, newname):
	new_path = os.path.join(dirname, newname + '.opf')
	opf = os.path.join(dirname, 'metadata.opf')
	if os.path.exists(opf):
		if os.path.exists(new_path):
			print(f'Already renamed: {newname}.opf')
		else:
			print('Rename metadata.opf ...')
			os.rename(opf, new_path)
	else:
		print('Not found: {}'.format(opf))

def get_cover(dirname, newname, asin):
	new_path = os.path.join(dirname, newname + '.jpg')
	cover_jpg = os.path.join(dirname, 'cover.jpg')
	if os.path.exists(cover_jpg):
		print('Rename cover.jpg...')
		os.rename(cover_jpg, new_path)
	else:
		print('Fetching book cover...')
		img_url = 'http://images-jp.amazon.com/images/P/' + asin + '.09.LZZZZZZZ.jpg'
		with urllib.request.urlopen(img_url) as response:
			with open((new_path), 'wb') as fp:
				shutil.copyfileobj(response, fp)
	# print('' + newname + '.jpg')
	print('done.')

# https://stackoverflow.com/questions/56401166/using-python-textwrap-shorten-for-string-but-with-bytes-width
_ELLIP = '_'
_MIN_WIDTH = len(_ELLIP.encode())

def shorten_to_bytes_width(text: str, width: int) -> str:
	clipped = False
	text = " ".join(text.split()) # reduce multiple spaces
	# Ref: https://stackoverflow.com/a/56401167/
	width = max(_MIN_WIDTH, width)	# This prevents ValueError if width < _MIN_WIDTH
	while (len(text.encode()) + _MIN_WIDTH) > width:
		clipped = True
		text = text[:-1].strip()
	assert (len(text.encode()) + _MIN_WIDTH) <= width
	if clipped:
		return text + _ELLIP
	else:
		return text

if __name__ == "__main__":
	main()
