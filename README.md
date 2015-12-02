# our story
for NaNoGenMo 2015

## output files!
[our story (pdf)](https://github.com/thricedotted/ourstory/blob/master/our_story.pdf)
[our story (txt)](https://github.com/thricedotted/ourstory/blob/master/our_story.txt)

(don't try to read it in github's pdf viewer thing, it's too long and makes it slow :| )

## author's statement or w/e
hi i threw this together at the very last minute. it is the product of starting nanogenmo somewhere between 4 and 8pm on november 30.

the novel has three parts: PAST, PRESENT, and FUTURE. each page alternates between a poem about you, and a poem about me. in sum they form our story.

the data i used for this is from the [Google Syntactic N-grams](http://googleresearch.blogspot.com/2013/05/syntactic-ngrams-over-time.html). they are sort of like the google books n-grams but bigger and also with extra annotations that i did not take much advantage of this time around. using this data caused a lot of stuff about christ to come up because n-grams from the bible sure happen a lot.

although i am sharing the code for the novel, it will not be runnable since it also depends on a database for the n-grams that is far too large to include.

however, the algorithm behind this is not complex. on each page, a word (verb, adjective, or noun) is sampled for what you/i were/are/will be. the algorithm then searches for n-grams containing this word, paired with a random preposition. these phrases are collected, shuffled randomly, and assembled into a poem. there are some things that go into it to make it look nice, but no fancy linguistic things here -- just search, shuffle, glue together.

this was fun and i'm happy i got to do something for #nanogenmo this year. i hope you find it interesting!
