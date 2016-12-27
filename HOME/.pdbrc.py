from pdb import DefaultConfig, Color
from pygments.token import Keyword, Name, Comment, String, Error, \
     Number, Operator, Generic, Token, Whitespace

class Config(DefaultConfig):
    """This is a config for pdb++."""

    bg = 'light'
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
    sticky_by_default = True

    def setup(self, pdb):
        Pdb = pdb.__class__
        Pdb.do_st = Pdb.do_sticky
