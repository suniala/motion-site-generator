# coding=utf-8
from optparse import OptionParser
from os import listdir
from os import makedirs
from os.path import isfile, join, relpath, exists
from string import Template

TMPL_PAGE = Template('''
<html>
<head>
<meta HTTP-EQUIV="Content-Type" content="text/html; charset=utf-8">
<title>$title</title>
</head>
<body>
<h1>$title</h1>
$content
</body>
</html>
''')

TMPL_DAYS = Template('''
<ul>
$items
</ul>
''')

TMPL_DAY = Template('''
<li><a href="$url">$label</a></li>
''')

TMPL_EVENTS = Template('''
<div>
<a href="..">takaisin</a>
</div>
<div>
$items
</div>
''')

TMPL_EVENT = Template('''
<div>
<h2>$label</h2>
<a href="$event_url">
  <img src="$img_url" style="width: 320px;" />
</a>
</div>
''')

TMPL_PICTURES = Template('''
<div>
<a href="..">takaisin</a>
</div>
<div>
$items
</div>
''')

TMPL_PICTURE = Template('''
<img src="$img_url" />
''')


def parse_archive(path):
    archive = []

    day_names = [f for f in listdir(path) if not isfile(join(path, f))]
    day_names.sort()

    for day_name in day_names:
        day = {'day': day_name, 'events': []}
        archive.append(day)

        day_path = join(path, day_name)
        event_names = [f for f in listdir(day_path) if not isfile(join(day_path, f))]
        event_names.sort()

        for event_name in event_names:
            event_path = join(day_path, event_name)
            picture_names = [f for f in listdir(event_path) if isfile(join(event_path, f))]
            picture_names.sort()

            if picture_names:
                event = {'event': event_name, 'pictures': []}
                day['events'].append(event)
                event['pictures'] = picture_names

    return archive


def render_root_index(archive):
    return TMPL_PAGE.substitute(
        title='Arkisto',
        content=TMPL_DAYS.substitute(
            items=''.join(
                TMPL_DAY.substitute(url=day['day'], label=day['day']) for
                day in archive)
        ))


def render_day_index(site_path, archive_root_path, day):
    return TMPL_PAGE.substitute(
        title='Päivä %s' % (day['day']),
        content=TMPL_EVENTS.substitute(
            items=''.join(
                TMPL_EVENT.substitute(
                    label='Tapahtuma %s (%d kuvaa)' % (event['event'], len(event['pictures'])),
                    event_url=event['event'],
                    img_url=relpath(join(archive_root_path, day['day'], event['event'], event['pictures'][0]),
                                    join(site_path, day['day']))
                )
                for event in day['events'])
        ))


def render_event_index(day_site_path, day_root_path, event):
    return TMPL_PAGE.substitute(
        title='Tapahtuma %s' % (event['event']),
        content=TMPL_PICTURES.substitute(
            items=''.join(
                TMPL_PICTURE.substitute(
                    img_url=relpath(join(day_root_path, event['event'], p),
                                    join(day_site_path, event['event']))
                )
                for p in event['pictures'])
        ))


def write(site_path, html):
    with open(site_path, 'w') as f:
        f.write(html)


def write_site(site_path, archive_root_path, archive):
    root_index = render_root_index(archive)

    if not exists(site_path):
        makedirs(site_path)

    write(join(site_path, 'index.html'), root_index)

    for day in archive:
        day_dir_path = join(site_path, day['day'])
        if not exists(day_dir_path):
            makedirs(day_dir_path)
        write(join(day_dir_path, 'index.html'), render_day_index(site_path, archive_root_path, day))

        for event in day['events']:
            event_dir_path = join(day_dir_path, event['event'])
            if not exists(event_dir_path):
                makedirs(event_dir_path)
            write(join(event_dir_path, 'index.html'),
                  render_event_index(join(site_path, day['day']), join(archive_root_path, day['day']), event))


def main():
    parser = OptionParser()
    parser.add_option("-o", "--output",
                      dest="output_path",
                      help="output directory")
    parser.add_option("-i", "--input",
                      dest="input_path",
                      help="input directory")

    (options, args) = parser.parse_args()

    if not options.input_path or not options.output_path:
        parser.print_help()
        exit(2)

    archive = parse_archive(options.input_path)
    write_site(options.output_path, options.input_path, archive)


if __name__ == '__main__':
    main()
