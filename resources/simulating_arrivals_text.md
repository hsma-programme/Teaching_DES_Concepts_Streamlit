To start with, we're just going to assume people arrive at a consistent rate throughout all 24 hours of the day. This isn't very realistic, but we can refine this later. 


When a patient arrives, the computer will pick a random number from this distribution to decide how long it will be before the next patient arrives at our treatment centre. 


Where the bar is very high, there is a high chance that the random number picked will be somewhere around that value. 

Where the bar is very low, it's very unlikely that the number picked will be from around that area - but it's not impossible. 

So what this ends up meaning is that, in this case, it's quite likely that the gap between each patient turning up at our centre will be somewhere between 0 and 10 minutes - and in fact, most of the time, someone will turn up every 2 or 3 minutes. However, now and again, we'll get a quiet period - and it might be 20 or 30 minutes until the next person arrives. 

This is quite realistic for a lot of systems - people tend to arrive fairly regularly, but sometimes the gap will be longer. 

# Variability and Computers

Without getting too philosophical, the version of reality that happens is just one possible version!

Maybe we're going to get a really hot summer that means our department is busier due to heatstroke and people having accidents outside. 
Maybe it will rain all summer and everyone will stay indoors. 

And what if lots of people turn up really close together? How well does our department cope with that? 


So instead of just generating one set of arrivals, we will run the simulation multiple times. 

The first time the picks might be like this:

5 minute gap, 4 minute gap, 5 minute gap, 6 minute gap

The next time they might be like this:

4 minute gap, 25 minute gap, 2 minute gap, 1 minute gap

And so on. 

Because computers aren't very good at being truly random, we give them a little nudge by telling them a 'random seed' to start from. You don't need to worry about how that works - but if our random seed is 1, we will draw a different set of times from our distribution to if our random seed is 100. This allows us to make lots of different realities, 