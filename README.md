At Penn State Mac Admins 2017, Mike Lynn (aka frogor and pudquick) demonstrated something he built for the Hack-a-thon -- some code that reacts to a push-button Bluetooth beacon he obtained:

https://gist.github.com/pudquick/9797a9ce8ad97de6e326afc7c9894965

PSU Mac Admin attendees got a Tile Mate in their "swag bag" -- this is a BTLE device used to help people keep track of and locate items. It has a button, so I wanted to see if I could modify Frogor's code to work with the Tile device.

I was mostly successful -- try it and see.

If you've already set up your Tile device, to play with this code:

1) Turn off Bluetooth on your iPhone or Android phone you installed the Tile app on. (If you don't do this, the Tile device will talk only to the phone and this code won't see the needed Bluetooth LE advertisements.)

2) Run the tile_lock.py script.

3) Double-click the Tile logo on yout Tile Mate. Your Mac's screen should lock.

4) Wait 10-15 seconds until the Tile Mate stops beeping, then double-click the logo again. If the screen is still locked, a fake car alarm will go off.

As written, this code will react to _any_ Tile device in range.