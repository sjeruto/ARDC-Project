### Load Packages

library(tm)
library(tidyverse)
library(SnowballC)
library(wordcloud)
library(topicmodels)
library(text2vec)
library(e1071)
library(SentimentAnalysis)
library(readr)
library(textstem)
library(wordcloud2)
library(dplyr)


### Load data
rest_rev <- read_tsv("Restaurant_Reviews.tsv")

###Convert to VCorpus
corpus_rest_rev <-VCorpus(VectorSource(rest_rev$Review))

# Contents lookup
corpus_rest_rev[1]
class(corpus_rest_rev[1])
class(corpus_rest_rev[[1]])
corpus_rest_rev[[1]]$meta
corpus_rest_rev[[133]]$content

#Remove punctuation, replace them with an empty space.
corpus_rest_rev <- tm_map(corpus_rest_rev, removePunctuation)

#Transform all cases to lower case
corpus_rest_rev <- tm_map(corpus_rest_rev,content_transformer(tolower))

#Remove digits/numbers
corpus_rest_rev <- tm_map(corpus_rest_rev, removeNumbers)

#Remove stopwords from standard dictionary 
corpus_rest_rev <- tm_map(corpus_rest_rev, removeWords, stopwords("english"))

#Remove whitespaces
corpus_rest_rev <- tm_map(corpus_rest_rev, stripWhitespace)

# Look at output, compared to output before pre-processing
writeLines(as.character(corpus_rest_rev[[133]]))

#Stem document: Allowing us to group terms with the same base/origin

corpus_rest_rev <- tm_map(corpus_rest_rev,stemDocument)

# After analyzing resulting terms, remove additional stopwords manually selected
myStopwords <- c("word1","word2","word3","word4","word5")
corpus_rest_rev <- tm_map(corpus_rest_rev, removeWords, myStopwords)

# Look at output, compared to output before pre-processing, and pre-STEM

writeLines(as.character(corpus_rest_rev[[133]]))

##LEMMA
#lemmatest <-tm_map(corpus_rest_rev, textstem::lemmatize_strings)

#writeLines(as.character(lemmatest[[133]]))

#Create document-term matrix: 
#1. Frequency 
dtm <- DocumentTermMatrix(corpus_rest_rev)
#2. exclude terms based on freq and lenght
dtmr <-DocumentTermMatrix(corpus_rest_rev, control=list(wordLengths=c(3, 15),
                                                        bounds = list(global = c(3,200))))
#3. apply term frequency-inverse document frequency 
dtm_tfidf <- DocumentTermMatrix(corpus_rest_rev,control = list(weighting = weightTfIdf))


#Inspect the different DTM summaries
dtm
dtmr
dtm_tfidf

#Look at different segments of the DTMs
inspect(dtm[1:12,601:611])
inspect(dtmr[1:12,211:221])
inspect(dtm_tfidf[1:12,601:611])

#Conver to matrix by aggregating (sum) over columns
#to calculate term frequency over all documents.
freq <- colSums(as.matrix(dtm))
freqr <- colSums(as.matrix(dtmr))
freqtfidf <- colSums(as.matrix(dtm_tfidf))

#Check how many terms each DTM produces (remember one of them excluded terms based on lenght and freq)
length(freq)
length(freqr)
length(freqtfidf)


#Order the frequency outputs
ord <- order(freq,decreasing=TRUE)
ordr <- order(freqr,decreasing=TRUE)
ordtfidf <- order(freqtfidf,decreasing=TRUE)

#Look at the most frequently occurring terms
freq[head(ord)]
freqr[head(ordr)]
freqtfidf[head(ordtfidf)]

#Look at the least frequently occurring terms
freq[tail(ord)]
freqr[tail(ordr)]
freqtfidf[tail(ordtfidf)]

#list most frequent terms. Those with a frequency higher than 15.
findFreqTerms(dtm,lowfreq=15)
findFreqTerms(dtmr,lowfreq=15)
findFreqTerms(dtm_tfidf,lowfreq=15)

#correlations
findAssocs(dtm,"word1",0.1)
findAssocs(dtm,"word2",0.1)
findAssocs(dtm,"word3",0.1)
findAssocs(dtm,"word4",0.1)
findAssocs(dtm,"word5",0.1)
findAssocs(dtm,"word6",0.1)


findAssocs(dtmr,"word",0.1)
findAssocs(dtmr,"word",0.1)
findAssocs(dtmr,"word",0.1)
findAssocs(dtmr,"word",0.1)
findAssocs(dtmr,"word",0.1)
findAssocs(dtmr,"word",0.1)


findAssocs(dtm_tfidf,"word",0.1)
findAssocs(dtm_tfidf,"word",0.1)
findAssocs(dtm_tfidf,"word",0.1)
findAssocs(dtm_tfidf,"word",0.1)
findAssocs(dtm_tfidf,"word",0.1)
findAssocs(dtm_tfidf,"word",0.1)


#histogram ordered by frequency

wf=data.frame(term=names(freqtfidf),occurrences=freqtfidf)
wf2= subset(wf, occurrences>30)

ggplot(wf2, aes(reorder(term,occurrences), occurrences))+
  geom_bar(stat="identity", fill="#3E76A8")+
  theme(panel.background = element_blank(), axis.ticks = element_blank())+
  labs(x = "Term",
       y = "Occurrences", 
       title = "Most Frequent Terms")


#wordcloud
set.seed(50)
df <- data.frame(word = names(freq),freq=freq)
sorteddf <- df[order(-freq),]
wordcloud2(data=sorteddf, size=1.6, color='random-dark') ####this one

##Experiment with ngrams (bigrams and trigrams)

BigramTokenizer <-  function(x) unlist(lapply(ngrams(words(x), 2), paste, collapse = " "), use.names = FALSE)
dtmbi <- DocumentTermMatrix(corpus_rest_rev, control = list(tokenize = BigramTokenizer))
freqbi <- colSums(as.matrix(dtmbi))
ordbi <- order(freqbi,decreasing=TRUE)
freqbi[head(ordbi)]

TrigramTokenizer <-  function(x) unlist(lapply(ngrams(words(x), 3), paste, collapse = " "), use.names = FALSE)
dtmtri <- DocumentTermMatrix(corpus_rest_rev, control = list(tokenize = TrigramTokenizer))
freqtri <- colSums(as.matrix(dtmtri))
ordtri <- order(freqtri,decreasing=TRUE)
freqtri[head(ordtri)]

##Check how many terms each ngram produces
length(freqbi)
length(freqtri)

#inspect most frequently occurring terms, with multiple appearances (at least 3)
findFreqTerms(dtmbi,lowfreq=3)
findFreqTerms(dtmtri,lowfreq=3)

### Sentiment Analysis

rest_revsa <- rest_rev
rest_revsa$Liked <-as.numeric(rest_rev$Liked)

# Create DTM
corpus_rest_rev2 <-VCorpus(VectorSource(rest_revsa$Review))
dtmsa <- DocumentTermMatrix(corpus_rest_rev2, control = list(weighting = weightTfIdf))

#Perform sentiment analysis
sentiment <- analyzeSentiment(dtmsa, 
                              rules=list(
                                "SentimentLM"=list(
                                  ruleSentiment, loadDictionaryLM()
                                ),
                                "SentimentQDAP"=list(
                                  ruleSentiment, loadDictionaryQDAP()
                                )
                              )
)

# Extract dictionary-based sentiment according to the QDAP dictionary
sentiment$SentimentQDAP

# Check sentiment direction (positive, neutral and negative)
direction <- convertToDirection(sentiment$SentimentQDAP)



### TOPIC MODELLING
#After getting the DTM

####

#Topic models
library(topicmodels)


#Run LDA using Gibbs Sampling
# Gibbs Sampling is a "Markov Chain Monte Carlo" algorithm that is often used to
# to approximate a probability distribution. See: https://en.wikipedia.org/wiki/Gibbs_sampling
# It works by performing a random walk in such a way that reflects the 
# characteristics of a desired distribution.
#
# The burn-in period is used to ensure that we start from a representative point. There
# is some controversy about the need to use burn-in periods. See: 
# https://www.johndcook.com/blog/2011/08/10/markov-chains-dont-converge/ for example
# We'll ignore the controversy and set...
burnin <- 1000
# and perform 2000 iterations (after burn-in)...
iter <- 2000
#..taking every 500th one for further use. This "thinning" is done to ensure that
# samples are not correlated.
thin <- 500
#We'll use 5 different, randomly chosen starting points
nstart <- 5
#using random integers as seed. Feel free to change these
seed <- list(2003,5,63,100001,765)
#...and take the best run (the one with the highest probability) as the result
best <- TRUE

#Number of topics (try different numbers from, say 4 to 8 and see which one returns
# the best results)
k <- 6
#Patience, this WILL take a while....
#................
#.............
#..........
#......
#....
#..
ldaOut <- LDA(dtm,k, method="Gibbs", control=
                list(nstart=nstart, seed = seed, best=best, burnin = burnin, iter = iter, thin=thin))
topics(ldaOut)
ldaOut.topics <-as.matrix(topics(ldaOut))
write.csv(ldaOut.topics,file=paste("LDAGibbs",k,"DocsToTopics.csv"))
terms(ldaOut,8)
ldaOut.terms <- as.matrix(terms(ldaOut,8))
write.csv(ldaOut.terms,file=paste("LDAGibbs",k,"TopicsToTerms.csv"))
#Find probabilities associated with each topic assignment
topicProbabilities <- as.data.frame(ldaOut@gamma) 
write.csv(topicProbabilities,file=paste("LDAGibbs",k,"TopicProbabilities.csv"))
