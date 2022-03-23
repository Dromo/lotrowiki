#!/usr/bin/python3
"""
Modified pykibots defualt bot simple.py
Takes user as input and patrols their edits

Use global -simulate option for test purposes. No changes to live wiki
will be done.
"""
#
# (C) Drono 2022
#
import pywikibot
from pywikibot import pagegenerators
from pywikibot.bot import (
    BaseBot,
)


# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {'&params;': pagegenerators.parameterHelp}  # noqa: N816


class BasicBot(BaseBot):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.site = pywikibot.Site()

    def treat(self, page):
        """Load the given page, do some changes, and save it."""
        rcid = page['rcid']
        list(self.site.patrol(rcid))
        print(page['title'])

def main(*args: str) -> None:
    """
    Process command line arguments and invoke bot.

    If args is an empty list, sys.argv is used.

    :param args: command line arguments
    """
    options = {}
    # Process global arguments to determine desired site
    local_args = pywikibot.handle_args(args)

    # This factory is responsible for processing command line arguments
    # that are also used by other scripts and that determine on which pages
    # to work on.
    gen_factory = pagegenerators.GeneratorFactory()

    # Process pagegenerators arguments
    local_args = gen_factory.handle_args(local_args)

    # Parse your own command line arguments
    user = ''
    for arg in local_args:
        if arg.startswith('-puser'):
            user = arg[len('-puser '):]
        arg, sep, value = arg.partition(':')
        option = arg[1:]
        #if option in ('user'):
        #    if not value:
        #        pywikibot.input('Please enter a value for ' + arg)
        #    options[option] = value

        # take the remaining options as booleans.
        # You will get a hint if they aren't pre-defined in your bot class
        #else:
        #    options[option] = True

    # The preloading option is responsible for downloading multiple
    # pages from the wiki simultaneously.
    #gen = gen_factory.getCombinedGenerator(preload=True)
    if not user:
        print("patrol.py > Please specify user: -puser=User")
        return
    site = pywikibot.Site()
    gen = site.recentchanges(user=user, patrolled=False)
    if gen:
        # pass generator and private options to the bot
        bot = BasicBot(generator=gen, **options)
        bot.treat_page_type = dict
        bot.run()  # guess what it does
    else:
        pywikibot.bot.suggest_help(missing_generator=True)


if __name__ == '__main__':
    main()
