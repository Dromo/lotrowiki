#!/usr/bin/python
"""
Use global -simulate option for test purposes. No changes to live wiki
will be done.

The following parameters are supported:

-always           The bot won't ask for confirmation when putting a page
-summary:         Set the action summary message for the edit.

"""
#
# (C) Drono 2021
#
from __future__ import absolute_import, division, unicode_literals

import pywikibot
import mwparserfromhell as mwparser
from pywikibot import pagegenerators
from pywikibot.bot import (
    SingleSiteBot,
    FollowRedirectPageBot
)


# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {'&params;': pagegenerators.parameterHelp}  # noqa: N816


class DronoBot(
    # Refer pywikobot.bot for generic bot classes
    SingleSiteBot,  # A bot only working on one site
    FollowRedirectPageBot
):

    def __init__(self, generator, **kwargs):
        """
        Initializer.

        @param generator: the page generator that determines on which pages
            to work
        @type generator: generator
        """
        # Add your own options to the bot and set their defaults
        # -always option is predefined by BaseBot class
        self.availableOptions.update({
            'summary': 'Drono-bot:Removing parameters with empty worth',
        })

        # call initializer of the super class
        super(DronoBot, self).__init__(site=True, **kwargs)
        # assign the generator to the bot
        self.generator = generator

    def treat_page(self):
        """Load the given page, do some changes, and save it."""
        text = self.current_page.text

        ################################################################
        # NOTE: Here you can modify the text in whatever way you want. #
        ################################################################
        # Test bot for removing empty parameters and empty worth parameters

        wikicode = mwparser.parse(text)
        templates = wikicode.filter_templates()
        for template in templates:
            if template.name == 'Recipe\n':
                for_remove = []
                for param in template.params:
                    value = str(template.get(param.name).value).strip()
                    #if value == "":
                        #for_remove.append(param)
                    if value == "{{worth|g=|s=|c=|dp=}}":
                        for_remove.append(param)
                    if value == "{{worth|lp=}}":
                        for_remove.append(param)
                    if value == "{{worth|tp=}}":
                        for_remove.append(param)
                for param in for_remove:
                    template.remove(param)

        self.put_current(wikicode, summary=self.getOption('summary'))


def main(*args):
    """
    Process command line arguments and invoke bot.

    If args is an empty list, sys.argv is used.

    @param args: command line arguments
    """
    options = {}
    # Process global arguments to determine desired site
    local_args = pywikibot.handle_args(args)

    # This factory is responsible for processing command line arguments
    # that are also used by other scripts and that determine on which pages
    # to work on.
    gen_factory = pagegenerators.GeneratorFactory()

    # Parse your own command line arguments
    for arg in local_args:
        if gen_factory.handleArg(arg):
            continue
        arg, sep, value = arg.partition(':')
        option = arg[1:]
        if option in ('summary'):
            if not value:
                pywikibot.input('Please enter a value for ' + arg)
            options[option] = value
        # take the remaining options as booleans.
        # You will get a hint if they aren't pre-defined in your bot class
        else:
            options[option] = True

    # The preloading option is responsible for downloading multiple
    # pages from the wiki simultaneously.
    gen = gen_factory.getCombinedGenerator(preload=True)
    if gen:
        # pass generator and private options to the bot
        bot = DronoBot(gen, **options)
        bot.run()  # guess what it does
    else:
        pywikibot.bot.suggest_help(missing_generator=True)


if __name__ == '__main__':
    main()
