#Seinfeld Fingerprinting


[CS591- Computational Audio](http://www.cs.bu.edu/~snyder/cs591/): Final Project 

##Running the program


After installing dependencies:

  - Runs on Python 2.7 on CSA2.BU.EDU server
  - Uses a MySQL DB (use createtable.sql)
  - Run Main.py 
  - Put sample in same directory 
  - Type 1 to fingerprint and 2 to recognize 

Example Run:

![](http://mattsauerbach.com/591/1.png)

##How it works

Consists of two main functions:

1. Fingerprinting an episode
2. Recognizing a sample 

####Fingerprinting

I followed methodologies taught in class, reviewed the fingerprinting powerpoint and used research papers that explain the Shazam method. The standard is taking the spectrogram from the Discrete Fourier Transform (DFT) and then apply a peak picking algorithm (finding local maxima). We find the local maxima at each window using a window size of 4096 and overlap of 2048. We then need to create a hash with the episode ID. This will be used during recognition when we apply the same fingerprinting algorithm to the sample and then match the hashes. To create a unique hash we take the local maxima and the delta between adjacent maximas. We then store these hashes in the database.  


Raw spectrogram from Seinfeld Episode (21min): The Frogger (Episode  9 Episode 18)

![](http://mattsauerbach.com/591/2.png)
(via Audacity) 

I first take the raw data and apply a low pass filter with a frequency threshold of  5,000 Hz. 
By analyzing this spectrogram, I was able to determine how to eliminate noise. After replaying many segments and playing with filters I determined the useful data, in TV recognition, was between 20 and 5,000 Hz. I found most dialogue was in this range, as well as a few extraneous sounds. Unfortunately, unhelpful signals such as laugh tracks remained after the low pass filter. 

![](http://mattsauerbach.com/591/3.png)

Here we can see how the low pass filter changes the spectrogram, amplifies frequencies lower than 5,000hz and removes any from above. This should help with accuracy and efficiency. 

When creating the spectrum, I used a window size of 4096 and an overlap of 2048. 

Next, I need to find a strong metric in each window, which will help me “fingerprint” each episode. The industry uses local maxima and there are a few ways to do this. After running the DFT on each window (taking into account overlap), we returns a 2D array of frequencies for each window. To find the local maxima I would find the highest frequency in each list.

It’s easier and more practical to use a method from the scipy library, which can find the highest peak very quickly.

Now we turn the correctly picked local maximas into hashes, so we can easily recall them. For hashing, I used the Dejavu library, which hashes the frequency and time difference between two adjacent peaks. Solely hashing frequencies would cause many collisions, so we also hash the delta’s of the adjacent peaks. 

Hash( peak frequencies, delta of adjacent peaks) 

![](http://mattsauerbach.com/591/4.png)

We then insert all the hashes into the database. I created my own MySQL DB for efficient read/writes. With only 13 episodes we have 42,000 fingerprints.    

DB Schema: 
Episodes (episode_id, episode_name)
Fingerprints (hash,episode_id, offset) 

Relate fingerprints.episode_id = episodes.episode_id 


Recognizing:

Input -> Raw Data -> Run Low Pass Filter- > Peak Picking -> Hash -> Find Matches -> determine episode with largest presence in the matches. 

Essentially, we run the input sample on the same algorithm used for fingerprinting, but instead of inserting the fingerprints into the database we look for matches. Using the episode id from the match we can determine the episode name. 

Example of recognition:

![](http://mattsauerbach.com/591/5.png)

Although we correctly identify “The Alternate Side”, we did find many incorrect matches. The highest match count came from id 13 so we return that episode. This sample was recorded on my computer’s mic from Youtube, which accounts for added noise. 
