At the moment, our model assumes that nurses and rooms to treat people in are the same thing.

In fact, that generally won't be the case - we might need more nurses than rooms to account for breaks, or people with different skills, or a fixed time for paperwork that is done outside of a room. 

There can also be issues that arise when a nurse is no longer needed, but the patient can't vacate the room yet - maybe they're waiting to be admitted into a general ward. This can lead to a lot of idle time for nurses who could otherwise be seeing patients if another room hasn't become available at that point. 

This is very important in a lot of real systems, so it's something we want to build into our model!

So now we need to check for two resources when a patient reaches the front of the queue:
- a nurse
- a room for them to be treated in 

To give us a better chance of wrapping our head around the impact of this, let's go back to a simpler version of the model for now. 