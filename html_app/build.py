#!/usr/bin/env python

"""The static asset pipeline for StarCellBio.

Usage:
  build.py
  build.py watch
  build.py -h | --help

Options:
  -h --help       Show this help screen.

"""

import logging
import os
import time

from docopt import docopt
from subprocess import call
from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler


ROOT = os.environ['PROJECT_HOME'] + '/html_app/'

global_update_index = True
js = dict()
css = dict()
TIME = '?_=' + str(int(time.time()))

CSS_PREFIX = '<link type="text/css" href="/static/'
CSS_SUFFIX = '" rel="Stylesheet" />\n'

JS_PREFIX = '<script type="text/javascript" src="/static/'
JS_SUFFIX = '" charset="UTF-8"></script>\n'

HTML_PREFIX = """
<!DOCTYPE html>
<html>
  <head>
    <META http-equiv='Content-Type' content='text/html; charset=UTF-8'>
    <meta http-equiv='content-type' content='text/html; charset=utf-8'>
    <title>StarCellBio Prototype</title>
"""
HTML_SUFFIX = """
</head>
<body>
  <div id='main'></div>
  <script>
    $(function() {
      starcellbio('#main', {});
    });
    window.clearCookie = function() {
      document.cookie = 'sessionid="invalid"'
    };
  </script>
</body>
"""
# add raven
HTML_SUFFIX += """
<script src='//cdn.ravenjs.com/1.1.11/jquery,native/raven.min.js'></script>
<script>
  Raven.config(
    'https://7845856fc975496e8dc2130b7140b19c@app.getsentry.com/19461',
    { whitelistUrls: ['starcellbio.mit.edu'] }
  ).install();
</script>
"""


def index_html():
    global css, js
    if js.has_key('js/jquery-1.7.2.min.js'):
        js.pop("js/jquery-1.7.2.min.js")
    if js.has_key("js/tinymce.min.js"):
        js.pop("js/tinymce.min.js")
    if js.has_key("js/jquery.tinymce.min.js"):
        js.pop("js/jquery.tinymce.min.js")
    if js.has_key("starcellbio.app.js"):
        js.pop("starcellbio.app.js")
    if js.has_key("swipe/Gruntfile.js"):
        js.pop("swipe/Gruntfile.js")
    if js.has_key("js/soyutils.js"):
        js.pop("js/soyutils.js")
    if js.has_key("master_model.js"):
        js.pop("master_model.js")

    css_join = (
        CSS_PREFIX +
        (TIME + CSS_SUFFIX + CSS_PREFIX).join(css.keys()) +
        TIME + CSS_SUFFIX
    )
    js_join = (
        JS_PREFIX +
        (TIME + JS_SUFFIX + JS_PREFIX).join(js.keys()) +
        JS_SUFFIX
    )
    js_join = JS_PREFIX + "../scb/get_user.js" + JS_SUFFIX + js_join
    js_join = JS_PREFIX + "starcellbio.app.js" + JS_SUFFIX + js_join
    js_join = JS_PREFIX + "js/soyutils.js" + JS_SUFFIX + js_join
    js_join = JS_PREFIX + "js/tinymce.min.js" + JS_SUFFIX + js_join
    js_join = JS_PREFIX + "js/jquery.tinymce.min.js" + JS_SUFFIX + js_join
    js_join = JS_PREFIX + "js/jquery-1.7.2.min.js" + JS_SUFFIX + js_join
    js_join = js_join + JS_PREFIX + "master_model.js" + JS_SUFFIX

    return HTML_PREFIX + css_join + js_join + HTML_SUFFIX


def update_index_html():
    f = open(
        "{}index.html".format(ROOT),
        "w"
    )
    f.write(index_html())
    f.close()
    print "new index.html"


def processor(path):
    """The translation pipeline for static assets.

    Arguments:
    path (str) -- the path to the static asset to process.

    """

    global global_update_index, css, js
    update_index = False
    path = path.replace("//", "/")
    url = path.replace(ROOT, "")
    if path.endswith(".js"):
        js[url] = 1
        update_index = True
    if path.endswith(".css"):
        css[url] = 1
        update_index = True
    if path.endswith(".soy"):
        infile = path
        outfile = "{}/gen/{}.js".format(
            os.path.dirname(infile),
            os.path.basename(infile)
        )
        call([
            "java",
            "-jar", "../tools/SoyToJsSrcCompiler.jar",
            "--outputPathFormat", outfile,
            infile
        ])
        print "compile soy {} ".format(path)
    if path.endswith(".gss"):
        infile = path
        outfile = "{}/gen/{}.css".format(
            os.path.dirname(infile),
            os.path.basename(infile)
        )
        call([
            "java",
            "-jar", "../tools/closure-stylesheets-20111230.jar",
            "--pretty-print", infile,
            "-o", outfile
        ])
        print "compile gss {} to {} ".format(infile, outfile)
    if path.endswith(".touch_index"):
        update_index_html()
    if update_index:
        global_update_index = True
        os.utime("{}.touch_index".format(ROOT), None)


def process_all():
    for subdir, _, files in os.walk(ROOT):
        for f in files:
            path = "{}/{}".format(subdir, f)
            processor(path)

    update_index_html()


class StaticConversionEventHandler(RegexMatchingEventHandler):
    """
    Match static files in the source directory and translate them.
    """

    def __init__(self):
        super(StaticConversionEventHandler, self).__init__(
            regexes=[".*\.(soy|gss)$"],
            ignore_directories=True,
            case_sensitive=False
        )

    def do_conversion(self, event):
        """
        Translate the static assets.
        """
        processor(event.src_path)
        update_index_html()

    def on_modified(self, event):
        """
        Process modified markdown files.
        """
        self.do_conversion(event)

    def on_created(self, event):
        """
        Process newly created markdown files.
        """
        self.do_conversion(event)


def watch(source):
    """
    Watch the source directory for changes until a KeyboardInterrupt is
    encountered.
    """
    observer = Observer()
    event_handler = StaticConversionEventHandler()
    observer.schedule(event_handler, source, recursive=True)

    logging.info("Starting watcher..")

    try:
        observer.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received; stopping watcher..")
        observer.stop()

    observer.join()


if __name__ == "__main__":
    args = docopt(__doc__)

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    if args['watch']:
        watch(".")
    else:
        process_all()