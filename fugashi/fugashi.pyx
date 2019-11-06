from mecab cimport (mecab_new2, mecab_sparse_tostr2, mecab_t, mecab_node_t,
        mecab_sparse_tonode, mecab_nbest_sparse_tostr)
from collections import namedtuple

# field names come from here:
# https://unidic.ninjal.ac.jp/faq
UnidicFeatures = namedtuple('UnidicFeatures', 
        ('pos1 pos2 pos3 pos4 cType cForm lForm lemma orth pron ' 
        'orthBase pronBase goshu iType iForm fType fForm').split(' '))

cdef class Node:
    cdef const mecab_node_t* c_node
    cdef str surface
    cdef object features

    def __init__(self):
        pass

    def __repr__(self):
        if self.stat == 0:
            return self.surface
        elif self.stat == 2:
            return '<BOS>'
        elif self.stat == 3:
            return '<EOS>'
        elif self.stat == 1:
            return '<UNK>' + self.surface
        else:
            return self.surface

    @property
    def surface(self):
        return self.surface
    
    @property
    def feature(self):
        if self.features is None:
            self.set_feature(self.c_node.feature)
        return self.features
    
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
    def pos(self):
        return "{},{},{},{}".format(*self.feature[:4])

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

    cdef void set_feature(self, bytes feature):
        fields = feature.decode('utf-8').split(',')
        if self.stat == 1: 
            # unks have fewer fields
            #XXX should this be '*' or ''?
            fields = fields + ([None] * 11)
        self.features = UnidicFeatures(*fields)

    @staticmethod
    cdef Node wrap(const mecab_node_t* c_node):
        cdef Node node = Node.__new__(Node)
        node.c_node = c_node

        # The surface gets freed so we need to copy it here
        # Also note it's not zero terminated.
        node.surface = c_node.surface[:c_node.length].decode('utf-8')

        return node

cdef class Tagger:
    cdef mecab_t* c_tagger

    def __init__(self, arg=''):
        arg = bytes(arg, 'utf-8')
        self.c_tagger = mecab_new2(arg)

    def parse(self, str text):
        btext = bytes(text, 'utf-8')
        out = mecab_sparse_tostr2(self.c_tagger, btext, len(btext)).decode('utf-8')
        # MeCab always adds a newline, and in wakati mode it adds a space.
        # The reason for this is unclear but may be for terminal use.
        # It's never helpful, so remove it.
        return out.rstrip()

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
            out.append(Node.wrap(node))

    def nbest(self, text, num=10):
        cstr = bytes(text, 'utf-8')
        out = mecab_nbest_sparse_tostr(self.c_tagger, num, cstr).decode('utf-8')
        return out.rstrip()

