# MTG

Statistical analysis of MTG Decks via simulating many games of magic across variants of decklists.  This is particularly useful for optimizing combo decks or damage output on very aggressive decks.  

Here's an overview of the work:
* **Core** - Engines for running simulations as well as OOP classes for Magic
* **Strategy** - Common strategy and gameplay to facillitate easy scripting for simulations
* **Generator** - Tools for auto-populating decklists for an Experiment.  Currently this allows you to iterate through ranges in a space of decklists.
* **Decks** - Decklists to run simulations upon
* **Experiments** - Stores permutations and hyperparameters for multi dimensional simulations
* **Results** - Stores results of Experiments
* **Simulations** - Entry points into running simulations
____

Inspired by giants and geniuses in our community I'll be self experimenting with my own mix of MTG Simulations

I'm attempting to combine the following great contributions:
* Frank Karsten's masterful contributions of applying statistics and Monte Carlo simulation to foundational MTG theory
* Allen Wu's concise and to the point Monte Carlo Simulation and it's impact on competitive MTG
* Dan Pope's wonderful Github example of beautiful OOP driven MTG simulations in python
* Thomas Oldham's use of visualizations to make MTG simulations more intuitive, interactive, and actionable

And I'll be putting my own spin on the above as well.  Contributing novel concepts of context driven simulations in
addition to ML driven optimization

----

**Examples of Possible Simulations**

**Overall Combo Rate - Odds of Cheating out Chandra's Incinerator**

![Overall Rate](Documentation/OverallRate.png)


**Average Damage output over 3 Turns**

![T2 Rate](Documentation/Damage%20Output_3%20Turns.png)

**Overall Combo Rate - Odds of hitting Turn 3 Throes of Chaos Combo**

![Throes Combo](Documentation/Throes%20Combo%20-%20Turn%203%20Rate.PNG)