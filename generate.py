#!/usr/bin/python
# -*- coding: utf-8 -*-

import codecs 
import os
import random
import sys
import time

from glob import glob
from collections import Counter

from ngramdb import NgramDb
from ngramdb.util import pprint_ngram_list

from bad_words import BAD_WORDS

reload(sys)
sys.setdefaultencoding('utf8')

start = time.time()

from spacy.en import English, LOCAL_DATA_DIR
data_dir = os.environ.get('SPACY_DATA', LOCAL_DATA_DIR)
nlp = English(data_dir=data_dir)

print("{} seconds to load nlp".format(time.time() - start))

follow_words = [
    "about",
    "from",
    "to",
    "in",
    "out",
    "toward",
    "towards",
    "away",
    "because",
    "that",
    "which",
    "into",
    "of",
    "with",
    "within",
    "without",
    "by",
    "for",
    "above",
    "below",
    "among",
    "around",
    "behind",
    "beside",
    "beyond",
    "between",
    "but",
    "and",
    "near",
    "on",
    "past",
    "through",
    "like",
    "unlike",
    "up",
    "down",
    "than"
]

def load_dicts(directory):
    big_dict = {}
    files = glob("{}/*".format(directory))

    for fn in files:
        person, ptense, pos = fn.split('/')[-1].split('_')
        tense = ptense_to_tense(ptense)

        if person not in big_dict:
            big_dict[person] = {}

        if tense not in big_dict[person]:
            big_dict[person][tense] = {}

        with codecs.open(fn, encoding='utf-8') as f:
            lines = [l.strip().split() for l in f.readlines()]
            if pos == 'VB' and tense == 'present':
                big_dict[person][tense][pos] = Counter(
                        {k: int(v) for k, v in lines 
                            if nlp(k)[0].tag_ in ('VBG', 'VBD', 'VBN')})
            elif pos == 'VB' and tense == 'future':
                big_dict[person][tense][pos] = Counter(
                        {k: int(v) for k, v in lines 
                            if nlp(k)[0].tag_ == 'VBP'})
            else:
                big_dict[person][tense][pos] = Counter(
                        {k: int(v) for k, v in lines})

    return big_dict

def ptense_to_tense(ptense):
    if ptense == 'will':
        return 'future'

    elif ptense in ('am', 'are'):
        return 'present'

    elif ptense in ('was', 'were'):
        return 'past'

    else:
        raise ValueError('invalid ptense "{}"'.format(ptense))

def tense_to_ptense(p, tense):
    i = {'past': 'was', 'present': 'am', 'future': 'will'}
    u = {'past': 'were', 'present': 'are', 'future': 'will'}

    if p == 'i':
        return i[tense]

    elif p == 'you':
        return u[tense]

    else:
        raise ValueError('invalid p "{}"'.format(p))

def get_continuations(big_dict, first):
    fragments = []
    results = []
    words = []

    second = random.choice(follow_words)

    words = [first, second]
    words_joined = ' '.join(words)

    print("querying {}".format(words_joined))

    results = db.create_and_run_query(words=words)

    if len(results) < 5:
        raise StandardError("not enough continuations found")

    results = [ng for ng in results if ng.surface != words_joined]

    surface = [ng.surface for ng in results if words_joined in ng.surface and
            not any(w in ng.surface for w in BAD_WORDS)]

    if len(results) < 5:
        raise StandardError("not enough continuations found")

    idxs = [s.index(words_joined) + len(words_joined) + 1 for s in surface]

    fragments = [s[idx:] for s, idx in zip(surface, idxs)
            if len(s) - idx > 3]

    return (second, sorted(set(fragments)))

def replace_pronoun(string, person='i'):
    if person == 'i':
        replacements = {
                "his": "your",
                "him": "you",
                "them": "you",
                "they": "you",
                "their": "your",
                "himself": "myself",
                "herself": "myself",
                }
    else:
        replacements = {
                "his": "my",
                "him": "me",
                "them": "me",
                "they": "i",
                "their": "my",
                "himself": "yourself",
                "herself": "yourself",
                }

    new_tokens = [s if s not in replacements else replacements[s] 
            for s in string.split()]

    return ' '.join(new_tokens)

db = NgramDb("nngm_dos")

big_dict = load_dicts('data')

def get_page_data(person, tense, pos, first=None):
    if first is None:
        first = random.choice(big_dict[person][tense][pos].most_common())[0]
    second, fragments = get_continuations(big_dict, first)

    k = random.randrange(10, 20)

    if len(fragments) > k:
        fragments = random.sample(fragments, k)

    return (first, second, sorted(fragments))

def assemble_lines(prefix, fragments, person):
    lines = []

    subprefixes = []
    for fragment in fragments:

        if any(all(t in l for t in fragment.split()) for l in lines):
            continue

        this_sp = ''
        for sp in subprefixes[:]:
            if fragment.startswith(sp):
                this_sp = sp
            else:
                subprefixes.remove(sp)

        if len(this_sp) > 0:
            fragment = fragment.replace(this_sp, '').strip()

        fragment = replace_pronoun(fragment, person)

        line = "{} {} {}".format(
                ' ' * (len(prefix) + 1),
                ' ' * (len(this_sp) + 1), 
                fragment)
        lines.append(line)

        subprefixes.append(fragment)

    random.shuffle(lines)

    connectives = [': ', '; ', ', ', ' -- ', ' and ', ' but '] + \
        [" {} ".format(w) for w in random.sample(follow_words, 5)]

    new_lines = []
    for line in lines:
        if random.random() < 0.1 and len(new_lines) > 0:
            new_lines[-1] = "{} {}".format(new_lines[-1], line.strip())

        elif random.random() < 0.1 and len(new_lines) > 0:
            cn = random.choice(connectives)
            new_lines[-1] = "{}{}{}".format(new_lines[-1], cn, line.strip())

        else:
            new_lines.append(line)

    new_new_lines = []
    for line in new_lines:
        if len(line) < 80:
            if random.random() < 0.3 and len(new_new_lines) > 0:
                new_new_lines.append('')
            new_new_lines.append(line)

    return new_new_lines

def generate_page(person, tense, pos, max_tries=5):
    first = ''
    do_not_even = ['be', 'have', 'is', 'has', 'are', 'do', 'am', "'m", "'s",
        "'re", "'ve", "'"]
    while len(first) == 0 or first in BAD_WORDS or first in do_not_even:
        first = random.choice(big_dict[person][tense][pos].most_common())[0]

    start = random.sample(['-', '+', '=', '>', '*', '^', '%', '$', '#', '@',
        '!', '.', '?', '&', ':', ';', '/', '|', '\\'], 3)
    prefix = "{} {} {}".format(person, tense_to_ptense(person, tense),
            first)

    if pos in ('JJ', 'NN') and tense == 'future':
        lines = ['  ' + l for l in lines if len(l) < 76]

    all_lines = [' '.join(start) + ' ' + prefix, '']

    tries = 0

    while len(all_lines) < 50 and tries < max_tries:
        try:
            _, second, fragments = get_page_data(person, tense, pos, first)
        except StandardError:
            all_lines.append("{:^80}".format('...'))
            all_lines.append('')
            tries += 1
            continue

        lines = assemble_lines(prefix, fragments, person)

        slice_idx = lines[0].index(lines[0].strip())
        new_line = "{}{} {}".format(lines[0][:slice_idx], second, lines[0][slice_idx:])

        if pos in ('JJ', 'NN') and tense == 'future':
            lines = ['  ' + l for l in lines if len(l) < 76]

        if len(new_line) < 80:
            lines[0] = new_line
        else:
            lines.insert(0, ' ' * (len(prefix) + 1) + second)

        all_lines.extend(lines)

    if len(all_lines) > 59:
        all_lines = all_lines[:59]
    else:
        all_lines = all_lines + (59 - len(all_lines)) * ['']

    all_lines = [l.replace(" 's", "'s") for l in all_lines]
    all_lines = [l + (' ' * (80 - len(l))) for l in all_lines]

    corrupters = [u'░', u'▒', u'▓']
    counter = Counter()

    final_lines = []
    for line in all_lines:
        tokens = [t for t in line.split() if len(t) > 3]

        new_line = line

        for t in tokens:
            counter[t] += 1
            if counter[t] > 2:
                corrupted_t = ''
                for letter in t:
                    if random.random() < (counter[t] - 1.) / (counter[t] + 1):
                        corrupted_t += random.choice(corrupters)
                    else:
                        corrupted_t += letter
                new_line = new_line.replace(t, corrupted_t)
        
        final_lines.append(new_line)

    return final_lines

def decorated_page(person, tense, pos, max_tries=5):
    start = time.time()

    lines = generate_page(person, tense, pos, max_tries)

    end = time.time()

    tokens = ' '.join(lines).split()

    decoration = "{:<40}".format(''.join(
        ['x' if t in ('i', 'my', 'me', 'myself') 
        else 'o' if t in ('you', 'your', 'yourself')
        else '' for t in tokens]))

    render_time = "{:>40}".format("({:.1f} s)".format(end - start))

    page_no = "{:^80}".format("[ {} ]".format(10))

    top = [decoration + render_time, ' ' * 80]
    bottom = [' ' * 80, page_no]

    return top + lines + bottom

def render_document():

    with codecs.open('test', 'w', encoding='utf-8') as f:
        f.write('')

    max_tries = 5

    book_lines = []
    total_tokens = 0
    paaage = 1

    front = [' ' * 80] * 63
    front[28] = "{:^80}".format("ooo xxxxx")
    front[30] = "{:^80}".format("our story")
    front[32] = "{:^80}".format("xxx ooooo")
    front[60] = "{:^80}".format("@thricedotted")
    front[61] = "{:^80}".format("#nanogenmo 2015")

    book_lines += front

    print("*** PAST ***")
    past = [' ' * 80] * 63
    past[30] = "{:^80}".format("PAST")

    book_lines += past
    paaage += 1

    tense = 'past'

    with codecs.open('test', 'a', encoding='utf-8') as f:
        for l in front:
            f.write('{}\n'.format(l))
        for l in past:
            f.write('{}\n'.format(l))

    while total_tokens < 20000:
        start = time.time()

        person = 'i' if paaage % 2 else 'you'
        pos = random.choice(['VB', 'JJ', 'NN'])

        try:
            lines = generate_page(person, tense, pos, max_tries)
        except StandardError:
            print("???? oh no idk")
            continue

        end = time.time()

        tokens = ' '.join(lines).split()
        total_tokens += len(tokens)

        decoration = "{:<40}".format(''.join(
            ['x' if t in ('i', 'my', 'me', 'myself') 
            else 'o' if t in ('you', 'your', 'yourself')
            else '' for t in tokens]))

        render_time = "{:>40}".format("({:.1f} s)".format(end - start))

        page_no = "{:^80}".format("[ {} ]".format(paaage))
        paaage += 1

        top = [decoration + render_time, ' ' * 80]
        bottom = [' ' * 80, page_no]

        book_lines += top + lines + bottom

        with codecs.open('test', 'a', encoding='utf-8') as f:
            for l in top + lines + bottom:
                f.write('{}\n'.format(l))

        print("tokens: {}".format(total_tokens))
        print("pages: {}".format(len(book_lines) // 63))

    print("*** PRESENT ***")
    present = [' ' * 80] * 63
    present[30] = "{:^80}".format("PRESENT")

    with codecs.open('test', 'a', encoding='utf-8') as f:
        for l in present:
            f.write('{}\n'.format(l))

    book_lines += present
    paaage += 1

    tense = 'present'

    while total_tokens < 40000:
        start = time.time()

        person = 'i' if paaage % 2 else 'you'
        pos = random.choice(['VB', 'JJ', 'NN'])

        try:
            lines = generate_page(person, tense, pos, max_tries)
        except StandardError:
            print("???? oh no idk")
            continue

        end = time.time()

        tokens = ' '.join(lines).split()
        total_tokens += len(tokens)

        decoration = "{:<40}".format(''.join(
            ['x' if t in ('i', 'my', 'me', 'myself') 
            else 'o' if t in ('you', 'your', 'yourself')
            else '' for t in tokens]))

        render_time = "{:>40}".format("({:.1f} s)".format(end - start))

        page_no = "{:^80}".format("[ {} ]".format(paaage))
        paaage += 1

        top = [decoration + render_time, ' ' * 80]
        bottom = [' ' * 80, page_no]

        book_lines += top + lines + bottom

        with codecs.open('test', 'a', encoding='utf-8') as f:
            for l in top + lines + bottom:
                f.write('{}\n'.format(l))

        print("tokens: {}".format(total_tokens))
        print("pages: {}".format(len(book_lines) // 63))

    print("*** FUTURE ***")

    future = [' ' * 80] * 63
    future[30] = "{:^80}".format("FUTURE")

    book_lines += future

    with codecs.open('test', 'a', encoding='utf-8') as f:
        for l in future:
            f.write('{}\n'.format(l))

    paaage += 1

    tense = 'future'

    while total_tokens < 50000:
        start = time.time()

        person = 'i' if paaage % 2 else 'you'
        pos = random.choice(['VB', 'JJ', 'NN'])

        try:
            lines = generate_page(person, tense, pos, max_tries)
        except StandardError:
            print("???? oh no idk")
            continue

        end = time.time()

        tokens = ' '.join(lines).split()
        total_tokens += len(tokens)

        decoration = "{:<40}".format(''.join(
            ['x' if t in ('i', 'my', 'me', 'myself') 
            else 'o' if t in ('you', 'your', 'yourself')
            else '' for t in tokens]))

        render_time = "{:>40}".format("({:.1f} s)".format(end - start))

        page_no = "{:^80}".format("[ {} ]".format(paaage))
        paaage += 1

        top = [decoration + render_time, ' ' * 80]
        bottom = [' ' * 80, page_no]

        book_lines += top + lines + bottom

        with codecs.open('test', 'a', encoding='utf-8') as f:
            for l in top + lines + bottom:
                f.write('{}\n'.format(l))

        print("tokens: {}".format(total_tokens))
        print("pages: {}".format(len(book_lines) // 63))

