# -*- coding: utf-8 -*-
import codecs
import getopt
import sys
import re

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

import traceback
defMappings = {

        u'\u0020' :  " ",
        u'\u0901' :  "M", #".N"
        u'\u0902' :  "M",
        u'\u0903' :  "H",
        u'\u0905' :  "a",
        u'\u0906' :  "aa",
        u'\u0907' :  "i",
        u'\u0908' :  "ii",
        u'\u0909' :  "u",
        u'\u090A' :  "uu",
        u'\u090B' :  "R",
        u'\u0960' :  "RR",
        u'\u090F' :  "e",
        u'\u0910' :  "ai",
        u'\u0913' :  "o",
        u'\u0914' :  "au",
        u'\u0915' :  "k",
        u'\u0916' :  "kh",
        u'\u0917' :  "g",
        u'\u0918' :  "gh",
        u'\u0919' :  "N",
        u'\u091A' :  "ch",
        u'\u091B' :  "Ch",
        u'\u091C' :  "j",
        u'\u091D' :  "jh",
        u'\u091E' :  "N",
        u'\u091F' :  "T",
        u'\u0920' :  "Th",
        u'\u0921' :  "D",
        u'\u0922' :  "Dh",
        u'\u0923' :  "N",
        u'\u0924' :  "t",
        u'\u0925' :  "th",
        u'\u0926' :  "d",
        u'\u0927' :  "dh",
        u'\u0928' :  "n",
        u'\u092A' :  "p",
        u'\u092B' :  "ph",
        u'\u092C' :  "b",
        u'\u092D' :  "bh",
        u'\u092E' :  "m",
        u'\u092F' :  "y",
        u'\u0930' :  "r",
        u'\u0932' :  "l",
        u'\u0935' :  "v",
        u'\u0936' :  "sh",
        u'\u0937' :  "Sh",
        u'\u0938' :  "s",
        u'\u0939' :  "h",
        u'\u093D' :  ".a",
        u'\u093E' :  "aa",
        u'\u093F' :  "i",
        u'\u0940' :  "ii",
        u'\u0941' :  "u",
        u'\u0942' :  "uu",
        u'\u0943' :  "R",
        u'\u0944' :  "RR",
        u'\u0947' :  "e",
        u'\u0948' :  "ai",
        u'\u094A' :  "o",
        u'\u094B' :  "o",
        u'\u094C' :  "au",
        u'\u094D' :  "h",
        u'\u0950' :  "OM",
        u'\u0964' :  "|",
        u'\u0963' :  "LR",
        u'\u0965' :  "||",
        u'\u0966' :  "0",
        u'\u0967' :  "1",
        u'\u0968' :  "2",
        u'\u0969' :  "3",
        u'\u096A' :  "4",
        u'\u096B' :  "5",
        u'\u096C' :  "6",
        u'\u096D' :  "7",
        u'\u096E' :  "8",
        u'\u096F' :  "9",
        u'\u097D' :  "?",
        u'\u200C' :  ""

    }



class Translator:



    def __init__(self, mapping=defMappings):
        global defMappings
        self._mapping = mapping

    def _translate(self,word):
        xlateWord = ""
        for c in word:
            if (c >= u'\u093E') and (c <= u'\u094D'):
                # 'a' was automatically added for vya~njanam 
                # so remove it if it is a maatraa or halant
                xlateWord = xlateWord[:-1]
            if c == u'\u094D':
                continue
            if self._mapping.has_key(c):
                xlateWord = xlateWord + self._mapping[c]
            elif ord(c) <= 0xFF:
                xlateWord = xlateWord + c
            else:
                print "CANNOT FIND character :%s: word=%s" % (hex(ord(c)),word)
                print "STACK : %s" % "\n".join(["%s:L%4d:%s:%s" % elem  for elem in traceback.extract_stack()])
                if hex(ord(c)) == 0xFEFF:
                    continue
                exit
            if (c >= u'\u0915') and (c <= u'\u0939'):
                # add 'a' automatically since the character mapping 
                # for these is actually with 'a' - maatraa or halant follows
                xlateWord = xlateWord + "a"
        xlateWord = xlateWord.replace("kSh", "x")
        return xlateWord


    def translateWord(self, word, suffix=True):
        try:
            #print "word: %s" % word
            word.decode('ascii')
            if suffix:
                xlateWord = word + "(eng)"
            else:
                xlateWord = word
        except UnicodeEncodeError:
            # non-ascii - translate
            xlateWord = self._translate(word)
        xlateWord = xlateWord.replace('|','')
        return xlateWord

    def translateWords(self, words):
        words = [self.translateWord(word) for word in words]
        return [word for word in words if word ]


class HandlerFactory(object):
    @staticmethod
    def getInputHandler(type):
        if type == 's':
            return ShlokaInputHandler()
        elif type == 'd':
            return DictionaryInputHandler()
        elif type == 'w':
            return WordInputHandler()
        elif type == 'n':
            return NotesInputHandler()
        return None

    @staticmethod
    def getOutputHandler(format):
        return BabylonOutputHandler()

def getArgs():
    inputs = []
    output = None
    type = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:o:t:", ["input=", "output="])
    except getopt.GetoptError as err:
        print str(err)
        exit(2)
    for o,a in opts:
         if o == "-i":
             inputs.extend([a])
         elif o == "-t": #type
             type = a
             if type == 's' or type == 'w' or type == 'd' or type == 'n':
                 pass
             else:
                 print "Bad type arg (%s) - only s(hloka), n(otes) or w(ord) allowed" % a
                 exit (2)
         elif o == "-o":
             if output:
                 print "Cannot specify two output files"
             else:
                 output = a
         else:
              print("Error")
    if not inputs or not output or not type:
        print "Did not specify input and/or output and/or type"
        exit(2)
    return [inputs, output, type]


def readHeader(data):
    header = dict()
    hdrString = "HEADER:"
    while data.find(hdrString) == 0:
        (hdrLine, data) = data.split('\n',1)
        hdrLine = hdrLine[len(hdrString):]
        (k,v) = hdrLine.split('=',1)
        if k == 'skip':
            pass
        elif k == 'title':
            pass
        elif k == 'type':
            pass
        elif k == 'shlokakey': #shloka key e.g. "BG, 2, 2"
            pass
        else:
            print "bad header: %s" % (k)
            exit (2)
        header[k] = v.split(';')
    return (header, data)

class InputHandler(object):
    def removeMetaData(self, entry):
        pass

    def mergeEntries(self, wordList):
        pass

    def entrySeparator(self, data):
        return ""

    def processEntry(self, entry, headers):
        return []

class BabylonOutputHandler(object):
    def getDictionary(self, wordList):
        data = ""
        translator = Translator()
        #print "wordList: %s" % wordList
        for entry in wordList:
            words = entry['words']
            xlatedWords = translator.translateWords(words)
            #print "xlated: %s" % (xlatedWords)
            wordEntry = "|".join(xlatedWords)
            meaningEntry = entry['entry']
            meaningEntry = meaningEntry.rstrip('\n')
            data = data + "%s\n%s\n\n" % (wordEntry, meaningEntry)
        return data

class DictionaryInputHandler(InputHandler):
    # Dictionary entries are of this form
    # - this is not a =very= long sentence (too much;excessive)
    #
    def __init__(self):
        self.source = "unknown"

    def removeMetaData(self, entry):
        pass

    def mergeEntries(self, wordList):
        finalList = {}
        for dictEntry in wordList:
            words = dictEntry['words']
            for word in words:
                if word in finalList:
                    finalList[word] = finalList[word] + "<br><br>%s" % dictEntry['entry']
                else:
                    finalList[word] = dictEntry['entry']
        wordList = [ {'words': [word], 'entry':entry} for word,entry in finalList.iteritems() ]
        return wordList

    def entrySeparator(self, data):
        return data.split('\n')

    def processEntry(self, entry, headers):
        if 'title' in headers:
            self.source = "; ".join(headers['title'])

        # process useless lines
        if not entry or entry[0] == '#' or not entry.strip():
            return []
        
        # process src
        if 'title' not in headers:
            source = re.findall(r'\[([^]]*)\]', entry)
            if entry.find('- ') != 0 and source:
                self.source = "; ".join(source)
                return []
        
        # process main entry
        # - blah blah =bbb= abc def (syn1;syn2)
        if entry.find('- ') != 0:
            return []
        entry = entry[2:]
        mainWords = re.findall(r'=([^=]*)=', entry)
        synWords = re.findall(r'\(([^)]*)\)', entry)
        if synWords:
            tmp = []
            for w in synWords:
                tmp.extend(w.split(';'))
            mainWords.extend(tmp)
        if not mainWords :
            return []

        offset = entry.find('(')
        if offset != -1:
            entry = entry[:offset]
        entry = entry.replace('=', '').strip() + "%s<br>[%s]" % ("; ".join(mainWords),self.source)
        return [{'words': mainWords,  'entry':entry }]



class WordInputHandler(InputHandler):
    def __init__(self):
        self.src1 = "unknown"
        self.src2 = "unknown"

    def removeMetaData(self, entry):
        pass

    def mergeEntries(self, wordList):
        return wordList

    def entrySeparator(self, data):
        return data.split('\n')

    def processEntry(self, entry, headers):
        # process useless lines
        if not entry or entry[0] == '#' or not entry.strip():
            return []
        
        # process src
        if entry.split('['):
            srcs = entry.split('[')
            return []
        
        # process main entry
        if entry and entry.find("- ") == 0:
            entry = entry[2:]
            if entry.find('('):
                (usage,notes) = entry.split('(', 1)
                notes = notes.split('(')
                notes = [note for note in notes.lstrip(') ')]

class NotesInputHandler(InputHandler):

    def removeMetaData(self, entry):
        pass

    def mergeEntries(self, wordList):
        return wordList

    def entrySeparator(self, data):
        return data.split('\n-')

    # return array of dict with 'word' 'syn' 'entry'
    def processEntry(self, entry, headers):
        (words, notes) = entry.split('\n', 1)
        words = words.strip(' -') #remove '-' and spaces if any in beginning or end
        notes = notes.replace('\n', '<br>')
        return [{'words':words.split(';'), 'entry':"<br>"+notes}]

class ShlokaInputHandler(InputHandler):

    def __init__(self):
        self.translator = Translator()
        super(ShlokaInputHandler,self).__init__()


    def removeMetaData(self, entry):
        pass

    def mergeEntries(self, wordList):
        return wordList

    def entrySeparator(self, data):
        return data.split('\n\n')

    def createShlokaRef(self, entry, headers):
        if 'shlokakey' not in headers:
            return None
        num = self.getShlokaNum(entry, headers)
        if not num:
            return None
        num = num.split('-')
        keydata = headers['shlokakey'][0].split(',')
        fmt = "%%s"
        ref = keydata[0]
        for idx,val in enumerate(keydata[1:]):
            #return (keydata[0], keydata[1])
            if len(num) <= idx:
                break
            fmt = "%%s-%%0%sd" % val
            ref = fmt % (ref, int(self.translator.translateWord(num[idx], suffix=False)))
        return ref + u'।'

    def getShlokaNum(self, entry, headers):
        delimiter = u'॥'
        parts = entry.split(delimiter)
        ref = None
        if len(parts) > 2:
            if len(parts) == 3:
                idx = 1 # default (two occurences)
            else:
                for idx, part in enumerate(parts):
                    if len(part) > 9:
                        continue
                    elif len(part.strip()) > 0:
                        break
#            try:
#                if idx < len(parts):
#                    print "** MG ** idx=%d num : %s" % (idx,parts[idx])
#            except Exception as e:
#                print " error"
#                return None
            ref = "".join(c for c in parts[idx] 
                          if ((c >= u'\u0966') and (c <= u'\u096F') or
                              c.isdigit()) or c == "-")
            if not len(ref):
                ref = None
        #print "** MG ** ref=%s" % ref
        return ref

    # process the following blobs and return the following:
    # - blob (as string) as it should appear in dictionary
    # - words - list of words to be added for this entry
    #
    # process these blobs (separator or '^+ '):
    # पदार्थः , निर्देशनम् , समासः, तद्धितः , कृदन्तः
    #
    #  + पदपरिचयः
    #    पदम्=विश्लेषणम् (उदा० भज=भज्;कर्तरि;लोट्;म०पु०;ए०व०)
    #  + पदार्थः
    #  - शब्दः१=अर्थः१;अर्थः२
    #  - शब्दः२(-)=अर्थः१;अर्थः२(-)  '(-)' => exclude
    #  + निर्देशनम्
    #  ++ धातुः
    #  --- धातुः१ विवरणम्
    #  --- धातुः२ विवरणम्
    #  ++ समासः
    #  --- पदम् : विग्रहः (समासस्य नाम)
    #  ++ सन्धिः
    #  --- सन्धियुक्तपदानि : विग्रहः (सन्धेः नाम)
    #  ++ तद्धितः
    #  --- प्रत्ययः : शब्दः : विग्रहः : notes 
    #  ++ कृदन्तः
    #  --- प्रत्ययः : शब्दः : विग्रहः : notes  यथा 'क्त : सम्प्राप्त : सम्+प्र+आप्+क्त '
    #  यत्किमपि अत्र

    def _processBlobs(self, blobs):
        # needs to be tested -- for now just print as-is
        return (set(), "\n".join(blobs).replace('\n', "<br>"))
        wordsToAdd = set()
        entry = ""
        for blob in blobs:
            if not blob:
                continue
            print "Blob = %s" % blob[0:10]
            entry = entry + blob.split("\n")[0] + "\n"
            #if re.match(r'पदार्थः.*', blob):
            if blob.find(u'पदार्थः'):
                for line in blob.split("\n"):
                    (word, meaningPart) = line.split("=")
                    line.replace("(-)", "")
                    line.replace("=", " : ")
                    entry = entry + "\t" + line + "\n"
                    meanings = meaningPart.split(";")
                    meanings.extend(word)
                    for meaning in meanings:
                        if not meaning.find("(-)"):
                            wordsToAdd.add (meaning)
            for line in blob.split("\n")[1:]:
                line.replace("(-)", "")
                entry = entry + "\t" + line + "\n"
        #print "Entry: \n%s\nwordsToAdd=%s\n" % (entry, wordsToAdd)
        return (wordsToAdd, entry)

    # return array of dict with 'word' 'syn' 'entry'
    # format:
    # श्लोकोऽयम् अत्र लिख्यते ।
    # तृतीयचतुर्थौ पादौ वर्तेत अत्र ॥१॥
    #  ==
    #  -निष्कासयतु (all => sarvam nishkaashayatu) (' ' इत्यस्य अन्तरालः)
    #  +योजयतु (' ' इत्यस्य अन्तरालम् दत्त्वा यथा शब्दः१ शब्दः२ इत्यादयः
    #  ++पदच्छेदः (' ' इत्यस्य अन्तरालम् दत्त्वा) यथा शब्दः१ शब्दः२ इत्यादयः (=> अन्यत् किमपि श्लोकात् न भवति एते + विशेषाः ये सूचिताः किन्तु यत्किमपि निष्कासयितुं निर्देशः ते परित्यक्ताः भवन्ति => "-all" is implied )
    #  अन्यत् (as-is included)
    #  ----
    #  blobs ('\n+ ' separated) (structured/ interpreted)
    #
    def processEntry(self, entry, headers):
        #print "** MG ** entry: %s" % {'entry':entry}
        addThese = []
        deleteThese = []
        subentries = entry.split('\n====\n')
        if len(subentries) == 1:
            shloka = subentries[0]
            shloka = shloka.rstrip('\n')
            shloka = shloka.rstrip('=')
            notes = ""
            blob = ""
        else:
            shloka = subentries[0]
            notes = subentries[1]
            blobs = notes.split('\n----\n')
            if len(blobs) == 2:
                notes = blobs[0]
                #blob = blobs[1].replace('\n','<br>')
                #blobs = blob.split('\n+ ')
                (wordsToAdd, blob) = self._processBlobs(blobs[1].split('+ '))
                addThese.extend(wordsToAdd)
            else:
                blob = ""
        #shloka = shloka.translate(None, '\u0964\u0965') # TBD
        # strip char after || so shloka = shloka.rsplit(";", 2)[0]
        #double = u"।।"
        #single = u"।"
        shloka.replace('\n', '')
        verses = shloka.split(u'॥')
        verses = [verse for verse in verses if len(verse) > 10 ]
        shloka = " ".join(verses)
        shloka.replace(u'॥', '')
        shloka.replace(u'।', '')
        words = set(shloka.split())
        #print ("** MG ** words=%s" % words)
        noteLines = notes.split('\n')
        title = ""
        if 'skip' in headers:
            deleteThese.extend(headers['skip'])
        if 'title' in headers:
            title = "; ".join(headers['title'])
        for note in noteLines:
            if note:
                if note[0] == "-":
                    #print "Delete these : %s" % note[1:]
                    deleteThese.extend([word.strip() for word in note[1:].split(';') if word.strip()])
                    #print "Delete these :%s:" % ",".join(deleteThese)
                elif note[0:2] == '++':
                    addThese.extend([word.strip() for word in note[2:].split(' ') if word.strip()])
                    words = set([]) # if ++ (पदच्छेदः) exists then wipe out actual words
                elif note[0] == "+":
                    addThese.extend([word.strip() for word in note[1:].split(';') if word.strip()])
        if "all" in deleteThese:
            words = set([])
        for s in addThese:
            #print "** MG ** adding %s" % s
            words.add(s)
        if 'nokey' not in deleteThese:
            shlokaRef = self.createShlokaRef(entry, headers)
        else:
            shlokaRef = None
        if shlokaRef:
            words.add(shlokaRef)
        # we want to delete after we have added ('cause we might add from
        # ++ but may not want those
        if not 'all' in deleteThese:
            for d in deleteThese:
                if d in words:
                    words.remove(d)
        notes = [note  for note in noteLines
                 if note and len(note) >= 2 and
                 note[0:2] == "++" or (note and note[0] != "-" and note[0] != "+" and note[0] != ".")]
        notes = '<br>'.join(notes)
        if notes:
            notes = entry.split('\n====\n')[0].replace('\n','<br>') + "<br>====<br>" + notes
        else:
            notes = entry.split('\n====\n')[0].replace('\n','<br>')
        if blob:
            notes = notes + "<br>----<br>" + blob
        notes = notes + "<br>[%s]" % title
        #notes = entry.split('\n==\n')[0].replace('\n','<br>') + "<br>====<br>" + notes + "<br>-----<br>" + blob + "<br>[%s]" % title
        
        #print "** MG ** words=%s\n\nnotes=\n%s\n" % (words, {'entry': notes})
        if not words:
            return None
        return [{'words': words, 'entry':notes}] # could have had 'words', 'word' as well - or multiple entries

def processFile(data, handler):
    (headers, data) = readHeader(data)
    shlokas = handler.entrySeparator(data)
    wordList = []
    for sh in shlokas:
        words = handler.processEntry(sh, headers)
        if words:
            wordList.extend(words)
    wordList = handler.mergeEntries(wordList)
    return wordList

def main():

    # open files
    (inputs, output, type) = getArgs()
    inputFileHandles = []
    try:
        for file in inputs:
            inputFileHandles.extend(
                [{"name":file,
                 "handle":codecs.open(file, 'r', encoding="utf8")}])
        outfile = codecs.open (output, 'w', 'utf-8')
    except Exception as err:
        print str(err)
        exit(2)

    # process entries
    wordList = []
    handler = HandlerFactory.getInputHandler(type)
    for file in inputFileHandles:
        print "Processing file: %s" % file['name']
        data = file['handle'].read()
        data = data.strip()
        data = data.rstrip()
        data = data.replace('\r','')
        wordList.extend(processFile(data, handler))
    handler.mergeEntries(wordList)

    # get output
    outputHandler = HandlerFactory.getOutputHandler('bbl')
    dictData = outputHandler.getDictionary(wordList)
    if dictData: 
        outfile.write("%s" % dictData)
        outfile.close()
    print "Wrote dictionary to %s" % (output)


main()
