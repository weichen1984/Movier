## Movier

### Summary

Movier studies the time evolution of featured movies produced in the US based on their screenplays/subtitles in terms of latent features. 

### Motivation

With a general interest in movies I am interested in exploring features other than the popular ones such as genres to categorize them. One possible candidate for such features is the way people speak. Possibly I can build a better recommendation system. Also, seeing people having different tastes in movies, I am interested in seeing how people's movie preferences change over time based on the new categories. This can also serve as a guideline for movie producers to choose among the screenplays. 

### Deliverables

The project will be demonstrated on a github page. Time evolution of latent features will be plotted with d3 visualization. Possible child pages for the recommendation systems of screenplays to produce for movie producers and movies to watch for moviers.

### Data Sources

General Information: [www.imdb.com](www.imdb.com) and [rotten tomatoes api](developer.rottentomatoes.com);  
Subtitles: [opensubtitle.org](www.opensubtitles.org) and [subscene](www.subscene.com);  
People's Input to Movies: ratings and box offices on [imdb](www.imdb.com), ratings and reviews on [rotten tomatoes](www.rottentomatoes.com) and ratings on Netflix (the Netflix Prize dataset).


### Process

1. Scrape data from the data sources as mentioned above and dump them into MongoDB;
2. Clean data so that each item corresponds to one IMDb ID and has attributes such as texts for subtitles, various ratings, release date, box office and etc;
3. Run TF-IDF on subtitles;
4. Perform a Non-Negative Matrix Factorization on the TF-IDF matrix;
5. Investigate the features and pick the top K1 latent features;
6. Cluster movies into K2 clusters based on these K1 features;
7. Analyze and visualize the change of these features over time;
8. Construct a similarity matrix among the movies and build a recommendation system based on the ratings on Netflix. 

