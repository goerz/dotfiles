import os
from pdb import DefaultConfig, Color
from pygments.token import Keyword, Name, Comment, String, Error, \
     Number, Operator, Generic, Token, Whitespace


def get_background():
    """Return the terminal background color ('light' or 'dark'), based on the
    COLORFGBG environement variable. Return None if the background color cannot
    be determined"""
    if 'COLORFGBG' in os.environ:
        try:
            bg_color_code = int(os.environ['COLORFGBG'].split(";")[-1])
            if bg_color_code == 8 or bg_color_code <= 6:
                return 'dark'
            else:
                return 'light'
        except (IndexError, TypeError, ValueError):
            return None
    else:
        return None


class Config(DefaultConfig):
    """This is a config for pdb++."""

    bg = get_background()
    if bg is None:
        bg = 'dark'
    filename_color = Color.darkgreen
    line_number_color = Color.brown
    current_line_color = int(Color.darkred)
    colorscheme = {
        Token:              ('',            ''),

        Whitespace:         ('lightgray',   'darkgray'),
        Comment:            ('lightgray',   'darkgray'),
        Comment.Preproc:    ('darkblue',        'turquoise'),
        Keyword:            ('darkblue',    'blue'),
        Keyword.Type:       ('darkblue',        'turquoise'),
        Operator.Word:      ('purple',      'fuchsia'),
        Name.Builtin:       ('darkblue',        'turquoise'),
        Name.Function:      ('darkgreen',   'green'),
        Name.Namespace:     ('darkblue',        'turquoise'),
        Name.Class:         ('',   ''),
        Name.Exception:     ('darkblue',        'turquoise'),
        Name.Decorator:     ('darkgray',    'lightgray'),
        Name.Variable:      ('darkblue',     'blue'),
        Name.Constant:      ('darkblue',     'blue'),
        Name.Attribute:     ('darkblue',        'turquoise'),
        Name.Tag:           ('blue',        'blue'),
        String:             ('darkgreen',       'brown'),
        Number:             ('darkblue',    'blue'),

        Generic.Deleted:    ('red',        'red'),
        Generic.Inserted:   ('darkgreen',  'green'),
        Generic.Heading:    ('**',         '**'),
        Generic.Subheading: ('*purple*',   '*fuchsia*'),
        Generic.Error:      ('_red_',        '_red_'),

        Error:              ('_red_',      '_red_'),
        }
    prompt = 'pdb> '
    sticky_by_default = False

    def setup(self, pdb):
        Pdb = pdb.__class__
        Pdb.do_st = Pdb.do_sticky
