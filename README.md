**Project status : 'Under correction'** <br />
Expected to be done in a day or two

# Exploring_Recommendation_Engine-Like_Netflix- 


## This is a full stack app with ML. This is a prototype, focusing on Recommendation Engine feature - purpose is to understand end-to-end development; Do not use the code for production!

About this project -

I wanted to understand Recommendation engines used in OTT platforms. So what better than building and learn about it. <br />
<br />
So, recommendation engines in OTT like Hulu, Netflix generally builds personalized contents(content focusing on that individual's interest); to do this we need to have data of the individual, what the person want to watch,the dislikes, the choices.

Now the OTT platforms have the user's data, atleast I can assume initially they might not; but as the user selects the contents, watches them and searches...all those is valuable data.

**So I designed my own architecture to fulfil my purpose**

### Now in my case, I have little resources, so what did I do? I dint want to download data from kaggle, so I spiced things a bit. I build a Netflix like UI (to certain level) asked couple of my friends to click on the movie thumbnails they like and watch trailers...(yeah..i added trailers too) but trailers are copyrighted you know, so I randomly put free videos, and asked some friends to watch full video, some to skip frames and some to close the videos.

Voila!! got the data and can code to interpret. Now I have these people's choices and dislikes - it is not statistically significant, its a small sample but hey thats good for my prototype.

What I do with this data? Enter **Collaborative** Filtering approach, its considered an ML algorithm.

Collaborative filtering? I will explain - Now i have these couple of my friend's data right, now if I could pair up friends who have similar likes and dislikes, I can recommend content that friend B watched to friend A because they are watching almost same content. This is collaborative and I filter the content data and recommend them. Briefly this is what it is.

**So all these data I stored in postgres, scoring them in this format : <br />
 clicked thumbnail? = value '1' <br />
 clicked video? = value '2' <br />
 watched full? = value '4' <br />
 skipped video? = '3' <br />
 closed video? = '2'**

Now I did some math, found patterns and created many pairs of collaborative friends.

Used that data to reflect the same in their UI.

Done!!

I implemented minimal front end because my focus is on recommendation engine.
