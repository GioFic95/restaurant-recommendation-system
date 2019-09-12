# Recommendation system for restaurants

## Project of the Machine Learning course
### Academic year 2018-2019
#### By Giovanni Ficarra and Leonardo Picchiami

***

We have devised a recommendation system for restaurants based on the 
[Yelp Dataset Challenge](https://www.yelp.com/dataset/challenge).

Our aim is to predict if a certain user will like a certain restaurant,
depending on characteristics of the restaurant, user’s taste
(derived from his previous reviews), opinion of similar users
(who gave similar votes to similar restaurants), trustworthiness of the
reviews.

In order to do so, we studied three papers,
that we used as the basis of our work:
1. [Restaurant Recommendation System, Ashish Gandhe](https://www.semanticscholar.org/paper/Restaurant-Recommendation-System-Gandhe/093cecc3e53f2ba4c0c466ad3d8294ba64962050);
2. [Machine Learning and Visualization with Yelp Dataset, Zhiwei Zhang](https://medium.com/@zhiwei_zhang/final-blog-642fb9c7e781)
    (with her [repo](https://github.com/zzhang83/Yelp_Sentiment_Analysis));
3. [Recommendation for yelp users itself, Wenqi Hou, Gauravi Saha, Manying Tsang](https://www.kaggle.com/wenqihou828/recommendation-for-yelp-users-itself).

We started from the data cleaning performed by Hou, Saha and Tsang (3),
then we applied the SVM model proposed by Zhang (2) to identify fake
reviews, and assigned to each review a “truth score”
(an indicator of the trustworthiness of the review),
so that we could use this score as a weight in the
computation of the historical features described by Gandhe (1).

After some further preprocessing we applied three machine learning models
to the obtained dataset: a Support Vector Machine, a Random Forest and a
Neural Network, from which we got our predictions.