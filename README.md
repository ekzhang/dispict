# Dispict: a creative aesthetics tool

Design a growing artistic exhibit of your own making. Bring your own labels and context.

**[dispict.com](https://dispict.com)** greets you with a blank canvas. You begin typing. Your writing becomes a _label_, and related artworks of the past appear spatially around the text you wrote. As you pan and zoom, you can add more labels to see how the artwork interpolates and shifts in aesthetic quality. Focus on a single work to see context: creator, setting, history, and descriptions.

## Motivation

There's currently so much excitement about computers helping us find creative inspiration by generating original art pieces from text prompts. But those lose the genuine, unique part of walking through an art museum and discovering unique _human insight_ and _intention_. What if computers could help us connect with great work done by artists of the past?

The Harvard Art Museums' online collection is huge, containing over 200,000 digitized works. This is far more than can be easily taken in by a single person. Instead we apply computation to what it's good at: finding patterns and connections.

**Creativity and curiosity require associative thinking.** Just like the technological innovations of centuries past have changed the aesthetic character of fine art from literal portraiture to more flexible modes of self-expression, _Dispict_ hopes to explore the honest, intimate relationship of humans to artwork and the creative process.

## Technical Details

_Dispict_ uses real-time machine learning. It's built on contrastive language-image pretraining with OpenAI's CLIP and nearest-neighbor search, served from Python with a dynamic React frontend.

## Acknowledgements

Created by Eric Zhang ([@ekzhang1](https://twitter.com/ekzhang1)) for [Neuroaesthetics](https://mbb.harvard.edu/people/nancy-etcoff) at Harvard. All code is licensed under [MIT](LICENSE), and data is generously provided by the [Harvard Art Museums](https://www.harvardartmuseums.org/) public access collection.

I learned a lot from Jono Brandel's [_Curaturae_](https://curaturae.com/) when designing this.
