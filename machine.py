import search
import random, re
from pattern.en import DEFINITE, tag, tokenize, conjugate, singularize, referenced, wordnet
from pprint import pprint

class Invention(object):
    def __init__(self, text):
        self.source_text = text
        self.title = self.create_gerund_title(text)
        self.create_first_line()
        self.create_abstract()
        self.create_illustrations()
        self.create_description()
        self.create_claims()

    def prefix(self):
        prefixes = ["system", "method", "apparatus", "device"]
        self.prefixes = random.sample(prefixes, 2)
        title = self.prefixes[0] + " and " + self.prefixes[1] + " for "
        if random.random() < .2:
            title = "web-based " + title
        return referenced(title)


    def create_gerund_title(self, text):
        search_patterns = [
                'VBG DT NN RB', 'VBG NNP * NP', 'VBG NNP * .',
                'RB VBG NNP', 'VBG JJ NP', 'VBG * JJ * NP', 'VBG * JJ *',
                'VBG * NN', 'VBG * JJ *? NP NP?', 'VBG * JJ? NP']

        gerund_phrases = search.search_out(text, search_patterns[-1])
        self.possible_titles = []
        for title in gerund_phrases:
            self.possible_titles.append(title)
        self.partial_title = random.choice(self.possible_titles)
        title = self.prefix() + self.partial_title
        self.set_keywords(self.partial_title)
        return title.capitalize()

    def set_keywords(self, title):
        words = tag(title)
        self.nouns = [word[0] for word in words if word[1] == 'NN']
        self.verbs = [word[0] for word in words if word[1] in ['VB', 'VBZ']]
        self.adjectives = [word[0] for word in words if word[1] == 'JJ']

    def create_first_line(self):
        templates = ['{0} is provided.', '{0} is disclosed.', 'The present invention relates to {0}.']
        self.first_line = random.choice(templates).format(self.title).capitalize()

    def find_lines(self):
        lines = search.search_out(self.source_text, '|'.join(self.nouns + self.verbs + self.adjectives))
        print lines

    def key_sentences(self):
        words = set(search.hypernym_search(self.source_text, 'instrumentality'))
        sents = tokenize(self.source_text)
        pat = re.compile(' ' + '|'.join(words) + ' ')
        sents = [s for s in sents if pat.search(s) != None]

        pprint(sents)
        pprint(words)


    def sentence_walk(self):
        output = []
        sents = tokenize(self.source_text)
        words = set(search.hypernym_search(self.source_text, 'artifact'))
        pat = re.compile(' ' + '|'.join(words) + ' ')
        sents = [s for s in sents if pat.search(s) != None]
        pprint(sents)

    def create_illustrations(self):
        self.illustrations = []
        templates = ["Figure {0} illustrates {1}.",
            "Figure {0} is a schematic drawing of {1}.",
            "Figure {0} is a perspective view of {1}.",
            "Figure {0} is an isometric view of {1}.",
            "Figure {0} schematically illustrates {1}.",
            "Figure {0} is a block diagram of {1}.",
            "Figure {0} is a cross section of {1}.",
            "Figure {0} is a diagrammatical view of {1}."]
        illustrations = list(set(search.search_out(self.source_text, 'DT JJ NP IN * NN')))
        self.unformatted_illustrations = illustrations
        for i in range(len(illustrations)):
            self.illustrations.append(random.choice(templates).format(i+1, illustrations[i]))

    def create_abstract(self):
        artifacts = search.hypernym_combo(self.source_text, 'artifact', "JJ NN|NNS")
        #artifacts +=search.hypernym_combo(self.source_text, 'material', "JJ NN|NNS")
        artifacts = set(artifacts)
        self.artifacts = artifacts
        words = []
        words = [referenced(w) for w in artifacts]
        self.abstract = self.title + ". "
        self.abstract += "The devices comprises "
        self.abstract += ", ".join(words) 

    def define_word(self, word):
        synsets = wordnet.synsets(word)
        if len(synsets) > 0:
            gloss = synsets[0].gloss
            if gloss.find(';') > -1:
                gloss = gloss[:gloss.find(';')]
            word = word + " (comprising of " + gloss + ") "
        return word

    def create_description(self):
        pat = 'VB|VBD|VBZ|VBG * NN IN * NN'
        #pat = 'PRP * VB|VBD|VBZ|VBG * NN'
        phrases = search.search_out(self.source_text, pat)
        conjugated_phrases = []
        for phrase in phrases:
            words = []
            for word, pos in tag(phrase):
                if pos in ["VBZ", "VBD", "VB", "VBG"]:
                    words.append(conjugate(word, "3sg"))
                #elif pos == "NN" and random.random() < .1:
                    #words.append(self.define_word(word))
                else:
                    words.append(word)
            conjugated_phrases.append(' '.join(words))

        artifacts = list(self.artifacts)

        sentence_prefixes = ["The present invention", "The device", "The invention"]
        paragraph_prefixes = ["The present invention", "According to a beneficial embodiment, the invention", "According to another embodiment, the device", "According to a preferred embodiment, the invention", "In accordance with an alternative specific embodiment, the present invention"] 
        i = 0
        self.description = ''
        for phrase in conjugated_phrases:
            line = ""
            if i == 0:
                line = paragraph_prefixes[0] + " " + phrase
            else:
                if random.random() < .1:
                    line = "\n\n" + random.choice(paragraph_prefixes) + " " + phrase
                else:
                    line = random.choice(sentence_prefixes) + " " + phrase
            self.description += line + ". "
            i += 1

    def create_claims(self):
        independent = '{0}. {1} for {2}, comprising:'
        dependent = '{0}. {1} of claim {2}, wherein said {3} comprises {4}.'

        self.claims = []
        claim_number = 0
        for prefix in self.prefixes:
            claim_number += 1
            claim = independent.format(
                claim_number, referenced(prefix).capitalize(), self.partial_title)
            terms = random.sample(list(self.artifacts),
                                  random.randint(2, min(len(self.artifacts), 5)))
            for term in terms[:-1]:
                claim += '\n\t' + referenced(term) + '; '
            claim += 'and \n\t' + referenced(terms[-1]) + '.'
            self.claims.append(claim)
            independent_claim_number = claim_number

            for term in terms:
                claim_number += 1
                claim = dependent.format(
                    claim_number,
                    referenced(prefix, article=DEFINITE).capitalize(),
                    independent_claim_number, term,
                    random.choice(self.unformatted_illustrations))
                self.claims.append(claim)

    def body_old(self):
        output = []
        useful_phrases = search.hypernym_combo(text, 'instrumentality', 'JJ? NP')
        random.shuffle(useful_phrases)
        random.shuffle(self.possible_titles)
        for i in range(len(self.possible_titles)):
            if (i < len(useful_phrases) and self.possible_titles[i] != self.partial_title):
                output.append(useful_phrases[i] + ' for ' + self.possible_titles[i])
        return output


    def format(self):
        print self.title
        print "\n\nABSTRACT\n\n"
        print self.abstract
        print '\n\nBRIEF DESCRIPTION OF THE DRAWINGS\n\n'
        for illustration in self.illustrations:
            print illustration
            print

        print "\n\nDETAILED DESCRIPTION OF THE PREFERRED EMBODIMENTS"
        #print "\n\nThe detailed description set forth below in connection with the appended drawings is intended as a description of presently-preferred embodiments of the invention and is not intended to represent the only forms in which the present invention may be constructed or utilized. The description sets forth the functions and the sequence of steps for using the invention in connection with the illustrated embodiments. However, it is to be understood that the same or equivalent functions and sequences may be accomplished by different embodiments that are also intended to be encompassed within the spirit and scope of the invention."
        print "\n"

        print self.description

        print "\n\nWhat is claimed is:"
        for claim in self.claims:
            print "\n%s" % claim


    def make_name_one(self):
        title_combos = search.hypernym_combo(text, 'instrumentality', 'JJ NP')
        title_combos = [t for t in title_combos if t.endswith('round') == False]
        title = random.choice(title_combos)
        return title

    def specific_title(self, title):
        words = title.split()
        for i in range(len(words)):
            word = words[i]
            new_word = search.random_hyponym(word)
            if len(new_word) > 0:
                words[i] = new_word
        return ' '.join(words)


if __name__ == '__main__':

    import sys

    text = sys.stdin.read().decode('ascii', errors='replace')
    print text
    invention = Invention(text)
    #for t in invention.possible_titles:
        #print invention.prefix() + t
    invention.format()
