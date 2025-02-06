"""
NIX_PATH=/home/nawal/data/tmp/old-nixpkgs/nixpkgs-20.09/ nix-shell



cd /home/nawal/data/languages
python combine.py
ebook-convert "epub/5MinuteItalianShortStories.epub" "epub/5MinuteItalianShortStories.mobi"
ebook-viewer epub/5MinuteItalianShortStories.mobi 
sudo mount /dev/sdc1  /media/
sudo cp epub/5MinuteItalianShortStories.mobi /media/documents/
sudo umount /media 

python combine.py
ebook-convert epub/ItalianShortStoriesforBeginnersItaTalkinItalian.epub epub/ItalianShortStoriesforBeginnersItaTalkinItalian.mobi
sudo mount /dev/sdc1  /media/
sudo cp epub/ItalianShortStoriesforBeginnersItaTalkinItalian.mobi /media/documents/
sudo umount /media 





nix-shell
python combine.py
ebook-convert epub/LaBandaDeiCinque01.epub epub/LaBandaDeiCinque01.mobi
sudo mount /dev/sdc1  /media/
sudo cp epub/LaBandaDeiCinque01.mobi /media/documents/
sudo umount /media 


nix-shell
python combine.py
ebook-convert epub/IlRagazzoInvisibileiten.epub epub/IlRagazzoInvisibileiten.mobi
sudo mount /dev/sdc1  /media/
sudo cp epub/IlRagazzoInvisibileiten.mobi /media/documents/
sudo umount /media 
sudo sync



https://pypub.readthedocs.io/en/latest/developer_interface.html
https://github.com/wcember/pypub


"""
# -*- coding: utf-8 -*-

import pypub
import cgi
import codecs


def main():
    out_dir = 'epub/'

    #it_fname = '5-minute-italian-short-stories-it.txt'
    #en_fname = '5-minute-italian-short-stories-en.txt'
    #out_name = '5MinuteItalianShortStories'
    
    #it_fname = 'Italian_ShortStoriesforBeginners-Ita-TalkinItalian-it.txt'
    #en_fname = 'Italian_ShortStoriesforBeginners-Ita-TalkinItalian-en.txt'
    #out_name = 'Italian_ShortStoriesforBeginners-Ita-TalkinItalian'

    #it_fname = 'ConTePartiro-it.txt'
    #en_fname = 'ConTePartiro-en.txt'
    #out_name = 'ConTePartiro'

    #it_fname = 'Volare-it.txt'
    #en_fname = 'Volare-en.txt'
    #out_name = 'Volare'


    #it_fname = 'La-banda-dei-cinque-01-Sull-isola-del-te-Enid-Blyton-it.txt'
    #en_fname = 'La-banda-dei-cinque-01-Sull-isola-del-te-Enid-Blyton-en.txt'
    #out_name = 'LaBandaDeiCinque01'

    it_fname = 'il_ragazzo_invisibile-it.txt'
    en_fname = 'il_ragazzo_invisibile-en.txt'
    out_name = 'IlRagazzoInvisibile-it-en'
    
    with codecs.open(it_fname, encoding='utf-8') as f1:
        it_lines = f1.read().split('\n')
    with codecs.open(en_fname, encoding='utf-8') as f2:
        en_lines = f2.read().split('\n')


    epub = pypub.Epub(out_name)

    max_lines = min(len(it_lines), len(en_lines))
    title_str = ''
    chapter_str = ''
    for i in range(max_lines):
        if en_lines[i].startswith('Chapter '):
            # write previous chapter
            if title_str != '':
                print(chapter_str)
                chapter = pypub.create_chapter_from_string(chapter_str, title=title_str)
                epub.add_chapter(chapter)
                print('---------')
            it_line = it_lines[i].encode('ascii', 'xmlcharrefreplace')
            en_line = en_lines[i].encode('ascii', 'xmlcharrefreplace')
            title_str = it_line
            chapter_str = '<h1>{}</h1>\n'.format(it_line)
            chapter_str += '<b>{}</b>\n'.format(en_line)
        else:
            if len(it_lines[i]) > 0 and len(en_lines[i]) > 0:
                it_line = it_lines[i].encode('ascii', 'xmlcharrefreplace')
                en_line = en_lines[i].encode('ascii', 'xmlcharrefreplace')
                chapter_str += '<p><b>' + it_line + '</b>\n'
                chapter_str += '<br>' + en_line + '</p>\n'

    chapter = pypub.create_chapter_from_string(chapter_str, title=title_str)
    epub.add_chapter(chapter)
    print('---------')

    epub.create_epub(out_dir, out_name)

if __name__=='__main__':
    main()

