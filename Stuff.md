# Notes #
  * Dead-reckoning --
    * for every type of motion, update relative position
    * we could monkeypatch - ugly implementation, beautiful interface
      * Myro will be monkeypatched to record positions
        * `_`updateSpeed? or some other "private" function
  * Obstacle Detection
    * How it works: sends out IR of a certain power
    * Light reflects, at a certain power
    * reflected luminosity is inverse-square to distance, and proportional to IR reflectivity of the obstacle -- so we'll do detector testing, and record reflectivities of different obstacle surfaces -- hopefully they'll be more or less the same
  * using dead-reckoning, we can draw arcs fitting the robot's projected path, and plop dots where we see obstacles
  * FOR LATER path-editing on interface -- in case the robot derps up, it would be nice to be able to rotate the path after any point

# Milestone #
To be done by Initial project demo
**Note: wiki says demo is due on Lab Session of October 31.**

Overview of what needs to be done by initial project demo:
  * voiding objects challenge
> > Must not touch the obstacle and find an alternative route
> > Obstacle is no taller than 10 cm
> > Chosen route to "go around" should be no more than 20 cm from the obstacle (minimize distance while still keeping it safe)
  * resent the advances on the project functionality
> > What has been done so far and been worked upon