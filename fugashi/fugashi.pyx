#cython: language_level=3
from fugashi.mecab cimport (mecab_new, mecab_sparse_tostr2, mecab_t, mecab_node_t,
        mecab_sparse_tonode, mecab_nbest_sparse_tostr, 
        mecab_dictionary_info_t, mecab_dictionary_info,
        mecab_model_new, mecab_strerror, mecab_dict_index)
from collections import namedtuple
import os
import csv
import shlex
import sys
from libc.stdlib cimport malloc, free

# field names can be found in the dicrc file distributed with Unidic or here:
# https://unidic.ninjal.ac.jp/faq

# 2.1.2 src schema
UnidicFeatures17 = namedtuple('UnidicFeatures17',
        ('pos1 pos2 pos3 pos4 cType cForm lForm lemma orth pron '
        'orthBase pronBase goshu iType iForm fType fForm').split(' '))

# 2.1.2 bin schema
# The unidic-mecab-2.1.2_bin distribution adds kana accent fields.
UnidicFeatures26 = namedtuple('UnidicFeatures26',
        ('pos1 pos2 pos3 pos4 cType cForm lForm lemma orth pron '
        'orthBase pronBase goshu iType iForm fType fForm '
        'kana kanaBase form formBase iConType fConType aType '
        'aConType aModeType').split(' '))

# schema used in 2.2.0, 2.3.0
UnidicFeatures29 = namedtuple('UnidicFeatures29', 'pos1 pos2 pos3 pos4 cType '
        'cForm lForm lemma orth pron orthBase pronBase goshu iType iForm fType '
        'fForm iConType fConType type kana kanaBase form formBase aType aConType '
        'aModType lid lemma_id'.split(' '))

cdef class Node:
    """Generic Nodes are modeled after the data returned from MeCab.

    Some data is in a strict format using enums, but most useful data is in the
    feature string, which is an untokenized CSV string."""
    cdef const mecab_node_t* c_node
    cdef str _surface
    cdef object features
    cdef object wrapper

    def __init__(self):
        pass

    def __repr__(self):
        if self.stat == 0 or self.stat == 1:
            return self.surface
        elif self.stat == 2:
            return '<BOS>'
        elif self.stat == 3:
            return '<EOS>'
        else:
            return self.surface

    @property
    def surface(self):
        if self._surface is None:
            self._surface = self.c_node.surface[:self.c_node.length].decode('utf-8')
        return self._surface
    
    @property
    def feature(self):
        if self.features is None:
            self.set_feature(self.c_node.feature)
        return self.features

    @property
    def feature_raw(self):
        return self.c_node.feature.decode('utf-8')
    
    @property
    def length(self):
        return self.c_node.length

    @property
    def rlength(self):
        return self.c_node.rlength

    @property
    def posid(self):
        return self.c_node.posid

    @property
    def char_type(self):
        return self.c_node.char_type

    @property
    def stat(self):
        return self.c_node.stat

    @property
    def is_unk(self):
        return self.stat == 1

    @property
    def white_space(self):
        # The half-width spaces before the token, if any.
        if self.length == self.rlength:
            return ''
        else:
            return ' ' * (self.rlength - self.length)
        
    cdef list pad_none(self, list fields):
        try:
            d = len(self.wrapper._fields) - len(fields)
        except AttributeError:
            d = 0
        return fields + [None] * d

    cdef void set_feature(self, bytes feature):
        raw = feature.decode('utf-8')
        if '"' in raw:
            # This happens when a field contains commas. In Unidic this only
            # happens for the "aType" field used for accent data, and then only
            # a minority of the time. 
            fields = next(csv.reader([raw]))
        else:
            fields = raw.split(',')
        fields = self.pad_none(fields)
        self.features = self.wrapper(*fields)

    @staticmethod
    cdef Node wrap(const mecab_node_t* c_node, object wrapper):
        cdef Node node = Node.__new__(Node)
        node.c_node = c_node
        node.wrapper = wrapper

        return node

cdef class UnidicNode(Node):
    """A Unidic specific node type.

    At present this just adds a convenience function to get the four-field POS
    value.
    """

    @property
    def pos(self):
        return "{},{},{},{}".format(*self.feature[:4])

    @staticmethod
    cdef UnidicNode wrap(const mecab_node_t* c_node, object wrapper):
        # This has to be copied from the base node to change the type
        cdef UnidicNode node = UnidicNode.__new__(UnidicNode)
        node.c_node = c_node
        node.wrapper = wrapper

        return node

def make_tuple(*args):
    """Take variable number of args, return tuple.

    The tuple constructor actually has a different type signature than the
    namedtuple constructor. This is a wrapper to give it the same interface.
    """
    return tuple(args)

FAILMESSAGE = """
Failed initializing MeCab. Please see the README for possible solutions:

    https://github.com/polm/fugashi

If you are still having trouble, please file an issue here, and include the
ERROR DETAILS below:

    https://github.com/polm/fugashi/issues

issueを英語で書く必要はありません。

------------------- ERROR DETAILS ------------------------"""

cdef str get_error_details(int argc, char** argv):
    """Instantiate a Model to get output from MeCab.

    Due to an upstream bug, errors in Tagger intialization don't give useful
    error output."""
    model = mecab_model_new(argc, argv)
    return mecab_strerror(NULL).decode('utf-8')

cdef void print_detailed_error(list args, int argc, char** argv):
    """Print guide to solving initialization errors."""
    print(FAILMESSAGE, file=sys.stderr)
    print('arguments:', args, file=sys.stderr)

    message = get_error_details(argc, argv)
    print('error message:', message, file=sys.stderr)
    print('----------------------------------------------------------')

cdef class GenericTagger:
    """Generic Tagger, supports any dictionary.

    By default dictionary features are wrapped in a tuple. If you want you can
    provide a namedtuple or similar container for them as an argument to the
    constructor.
    """

    cdef mecab_t* c_tagger
    cdef object wrapper

    def __init__(self, args='', wrapper=make_tuple, quiet=False):
        # The first argument is ignored because in the MeCab binary the argc
        # and argv for the process are used here.
        args = [b'fugashi', b'-C'] + [bytes(arg, 'utf-8') for arg in shlex.split(args)]
        cdef int argc = len(args)
        cdef char** argv = <char**>malloc(argc * sizeof(char*))
        for ii, arg in enumerate(args):
            argv[ii] = arg

        self.c_tagger = mecab_new(argc, argv)
        if self.c_tagger == NULL:
            # In theory mecab_strerror should return an error string from MeCab
            # It doesn't seem to work and just returns b'' though, so this will
            # have to do.
            if not quiet:
                print_detailed_error(args, argc, argv)
            free(argv)
            raise RuntimeError("Failed initializing MeCab")
        free(argv)
        self.wrapper = wrapper

    def __call__(self, text):
        """Wrapper for parseToNodeList."""
        return self.parseToNodeList(text)

    def parse(self, str text):
        btext = bytes(text, 'utf-8')
        out = mecab_sparse_tostr2(self.c_tagger, btext, len(btext)).decode('utf-8')
        # MeCab always adds a newline, and in wakati mode it adds a space.
        # The reason for this is unclear but may be for terminal use.
        # It's never helpful, so remove it.
        return out.rstrip()

    cdef wrap(self, const mecab_node_t* node):
        # This function just exists so subclasses can override the node type.
        return Node.wrap(node, self.wrapper)

    def parseToNodeList(self, text):
        cstr = bytes(text, 'utf-8')
        cdef const mecab_node_t* node = mecab_sparse_tonode(self.c_tagger, cstr)

        # A nodelist always contains one each of BOS and EOS (beginning/end of
        # sentence) nodes. Since they have no information on them and MeCab
        # doesn't do any kind of sentence tokenization they're not useful in
        # the output and will be removed here.

        # Node that on the command line this behavior is different, and each
        # line is treated as a sentence.
        out = []
        while node.next:
            node = node.next
            if node.stat == 3: # eos node
                return out
            out.append(self.wrap(node))

    def nbest(self, text, num=10):
        cstr = bytes(text, 'utf-8')
        out = mecab_nbest_sparse_tostr(self.c_tagger, num, cstr).decode('utf-8')
        return out.rstrip()

    @property
    def dictionary_info(self):
        """Get info on the dictionaries of the Tagger.

        This only exposes basic information. The C API has functions for more
        sophisticated access, though it's not clear how useful they are.

        The dictionary info structs will be returned as a list of dictionaries.
        If you have only the system dictionary that'll be the only dictionary,
        but if you specify user dictionaries they'll also be present.
        """
        infos = []
        cdef mecab_dictionary_info_t* dictinfo = mecab_dictionary_info(self.c_tagger)
        while dictinfo:
            info = {}
            info['filename'] = dictinfo.filename.decode('utf-8')
            info['charset'] = dictinfo.charset.decode('utf-8')
            info['size'] = dictinfo.size
            # Note this is generally not used reliably
            info['version'] = dictinfo.version
            dictinfo = dictinfo.next
            infos.append(info)
        return infos

def try_import_unidic():
    """Import unidic or unidic lite if available. Return dicdir."""
    try:
        import unidic
        return unidic.DICDIR
    except ImportError:
        try:
            import unidic_lite
            return unidic_lite.DICDIR
        except ImportError:
            # This is OK, just give up.
            return

cdef class Tagger(GenericTagger):
    """Default tagger. Detects the correct Unidic feature format.

    Unidic 2.1.2 (17 field) and 2.2, 2.3 format (29 field) are supported.
    """

    def __init__(self, arg=''):
        # Use pip installed unidic if available
        unidicdir = try_import_unidic()
        if unidicdir:
            mecabrc = os.path.join(unidicdir, 'mecabrc')
            arg = '-r "{}" -d "{}" '.format(mecabrc, unidicdir) + arg

        super().__init__(arg)

        fields = self.parseToNodeList("日本")[0].feature_raw.split(',')

        if len(fields) == 17:
            self.wrapper = UnidicFeatures17
        elif len(fields) == 26:
            self.wrapper = UnidicFeatures26
        elif len(fields) == 29:
            self.wrapper = UnidicFeatures29
        else:
            raise RuntimeError("Unknown dictionary format, use a GenericTagger.")

    # This needs to be overridden to change the node type.
    cdef wrap(self, const mecab_node_t* node):
        return UnidicNode.wrap(node, self.wrapper)

def create_feature_wrapper(name, fields, default=None):
    """Create a namedtuple based wrapper for dictionary features.

    This sets the default values for the namedtuple to None since in most cases
    unks will have fewer fields.

    The resulting type can be used as the wrapper argument to GenericTagger to
    support new dictionaries.
    """
    return namedtuple(name, fields, defaults=(None,) * len(fields))

def build_dictionary(args):
    args = [bytes(arg, 'utf-8') for arg in shlex.split(args)]
    cdef int argc = len(args)
    cdef char** argv = <char**>malloc(argc * sizeof(char*))
    for ii, arg in enumerate(args):
        argv[ii] = arg
    out = mecab_dict_index(argc, argv)
    free(argv)

