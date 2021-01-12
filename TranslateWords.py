import re
import csv
import logging
import time

logging.basicConfig()
logger = logging.getLogger("TranslateWords")


class WordNotFoundError(Exception):
    pass


class Translator:

    def __init__(self, word_list_file, dictionary_file, file_to_translate, output_file):
        self.word_list_file = word_list_file
        self.dictionary_file = dictionary_file
        self.file_to_translate = file_to_translate
        self.output_file = output_file
        self.translation_dictionary_cache = dict()
        self.translation_freq_lookup = dict()

    def search_dictionary(self, search_word) -> str:
        # load the dictionary into the memory if not already
        if len(self.translation_dictionary_cache) == 0:
            with open(self.dictionary_file) as dictionary_csv:
                reader = csv.reader(dictionary_csv, delimiter=',')
                for entry in reader:
                    word, translation = entry[0], entry[1]
                    self.translation_dictionary_cache[word] = translation

        if search_word in self.translation_dictionary_cache:
            translated_str = self.translation_dictionary_cache[search_word]
            self.translation_freq_lookup[search_word] = self.translation_freq_lookup.get(search_word, 0) + 1
            return translated_str
        else:
            raise WordNotFoundError(f"The word '{search_word}' couldn't be found")

    def start(self):

        search_terms = None
        with open(self.word_list_file) as words_file:
            search_terms = set([i.strip() for i in words_file.readlines()])
        logger.debug(f"Finished loading {len(search_terms)} search words into the memory")

        with open(self.file_to_translate) as non_translated_file, open(self.output_file, 'w') as output:
            # consider anything other than alphabets and numbers to be a delimiter
            regex_to_split_words = r'[^A-Za-z0-9]+'
            #*This Etext has certain copyright implications you should read*
            for non_translated_line in non_translated_file.readlines():
                translated_line = non_translated_line
                for word in re.split(regex_to_split_words, non_translated_line):
                    replaced_word = None
                    #This
                    if word.lower() in search_terms:
                        try:
                            replaced_word = self.search_dictionary(word.lower())
                            
                        except WordNotFoundError as e:
                            logger.error(e)
                            raise
                    if replaced_word:
                        if word.isupper():
                            replaced_word = replaced_word.upper()
                        elif word[0].isupper():
                            replaced_word = replaced_word[0].upper()
                        translated_line = re.sub(rf'({word})({regex_to_split_words})', rf'{replaced_word}\g<2>',
                                                 translated_line)
                output.write(translated_line)


if __name__ == '__main__':
    logger.setLevel(logging.INFO)
    word_list_file = "find_words.txt"
    dictionary_file = "french_dictionary.csv"
    file_to_translate = "t8.shakespeare.txt"
    output_file = "t8.shakespeare.txt.translated"

    t_start = time.perf_counter()
    translate_job = Translator(word_list_file, dictionary_file, file_to_translate, output_file)
    translate_job.start()
    t_end = time.perf_counter()

    logger.info(f"Totally replaced {len(translate_job.translation_freq_lookup)} unique words")
    total_words_replaced = 0
    for i in translate_job.translation_freq_lookup:
        total_words_replaced += translate_job.translation_freq_lookup[i]
    logger.info(f"Totally replaced {total_words_replaced} words")
    logger.info(f"Took {t_end-t_start:.3f} Seconds, "
                f"~{(t_end-t_start)/len(translate_job.translation_freq_lookup):.5f}s per unique word")
    logger.debug(f"Their frequency details are {translate_job.translation_freq_lookup}")


