import javax.microedition.lcdui.Image;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.game.GameCanvas;
import javax.microedition.lcdui.game.TiledLayer;
import java.util.Random;
import java.io.IOException;

public class MyGameCanvas
  extends GameCanvas implements Runnable {

	public MyGameCanvas() {
	  super(true);
	}

	public void start() {

	  try {

	    // create and load an image to the center

		pokemonImg = Image.createImage("/blinky.png");
		centerX = CENTER_X;


		//nowpokemon is on base line
		centerY = BASE;
		generateGameBackground();

	  } 
	  catch(IOException ioex) {
		 System.err.println(ioex);
	   }


	  Thread forever = new Thread(this);
	  forever.start();

	}

	public void run() {

	  // the graphics object for this canvas
	  Graphics g = getGraphics();

	  while(true) { // infinite loop

  	    // based on the structure

  		// first verify game state
  		checkGameState();

  		// check user's input
  		checkUserInput();

  		// update screen
  		updateGameScreen(getGraphics());

		// and sleep, this controls
		// how fast refresh is done
		try {
		  Thread.currentThread().sleep(25);
		} catch(Exception e) {}

	  }

	}



    // generates the background using TiledLayer
    private void generateGameBackground() throws IOException {

	// load the image
	bkndImg = Image.createImage("/bknd.png");

	// create the tiledlayer background
	background = new TiledLayer(5, 8, bkndImg, 32, 32);

	// array that specifies what image goes where
	int[] cells = {
	    1, 1, 1, 1, 1, // clouds
	    1, 1, 1, 1, 1, // clouds
	    1, 1, 1, 1, 1, // clouds
	    2, 2, 2, 2, 2, // lawn
	    2, 2, 2, 2, 2, // lawn
	    3, 3, 3, 3, 3, // water
	    3, 3, 3, 3, 3, // water
	    3, 3, 3, 3, 3  // water
	};

	// set the background with the images
	for (int i = 0; i < cells.length; i++) {
	    int col = i % 5;
	    int row = (i - col)/5;
	    background.setCell(col, row, cells[i]);
	}

	// set the location of the background
	background.setPosition(PLAYFIELD_ORIGIN_X, PLAYFIELD_ORIGIN_Y);
  
    }
	private void checkGameState() {

	}

	private void checkUserInput() {

	  // get the state of keys
	  int keyState = getKeyStates();

	  // calculate the position for x axis
	  calculateCenterX(keyState);
	  calculateCenterY(keyState);

	}


    private void buildGameScreen(Graphics g) {

	// set the drawing color to black
	g.setColor(0x000000);

	// draw the surrounding rectangle
	g.drawRect(PLAYFIELD_ORIGIN_X, PLAYFIELD_ORIGIN_Y, PLAYFIELD_WIDTH, PLAYFIELD_HEIGHT);

	// draw the base line
	g.drawLine(PLAYFIELD_ORIGIN_X, BASE, PLAYFIELD_ORIGIN_X + PLAYFIELD_WIDTH, BASE);

	// draw the maximum line to where pokemon can jump to
	g.drawLine(PLAYFIELD_ORIGIN_X, BASE - MAX_HEIGHT,
		   PLAYFIELD_ORIGIN_X + PLAYFIELD_WIDTH, BASE - MAX_HEIGHT);
	background.paint(g);

    }

	private void updateGameScreen(Graphics g) {

	  // the next two lines clear the background
	  g.setColor(0xFFFFFF);
	  g.fillRect(0, 0, getWidth(), getHeight());
	  buildGameScreen(g);
	  // draws the pokeman image in the current position
	  g.drawImage(pokemonImg, centerX, centerY, Graphics.HCENTER | Graphics.BOTTOM);

	  // this call paints off screen buffer to screen
	  flushGraphics();

	}

	private void calculateCenterX(int keyState) {

	  // determines which way to move and changes the
	  // x coordinate accordingly
	    if((keyState & LEFT_PRESSED) != 0) {
		centerX = Math.max(PLAYFIELD_ORIGIN_X + pokemonImg.getWidth()/2, centerX - dx);
	    }
	    else if((keyState & RIGHT_PRESSED) != 0) {
		centerX = Math.min(PLAYFIELD_ORIGIN_X + PLAYFIELD_WIDTH - pokemonImg.getWidth()/2, centerX + dx);;
	    }

	}



    private void calculateCenterY(int keyState) {

	// check if pokemon is going up
	if(up) {

	    // if yes, see if they have reached the current jump height
	    if((centerY > (BASE - jumpHeight + pokemonImg.getHeight()))) {

		// if not, continue moving them up
		centerY -= dy;
	    } else if(centerY == (BASE - jumpHeight + pokemonImg.getHeight())) {

		// if yes, start moving them down
		centerY += dy;

		// and change the flag
		up = false;

	    }

	} else {

	    // pokemon is going down. Check whether it has reached the base
	    if(centerY < BASE) {

		// keep going down
		centerY += dy;

	    } else if(centerY == BASE) {

		// pokemon has reached the base. new jump height is calculated which is not greater than MAX_HEIGHT
		int hyper = random.nextInt(MAX_HEIGHT + 1);

		// but make sure that this it is atleast greater than the image height
		if(hyper > pokemonImg.getHeight()) jumpHeight = hyper;

		// move the image up
		centerY -= dy;

		// and reset the flag
		up = true;

	    }
	}
    }

	// the pokemon image
	private Image pokemonImg;
	private Image bkndImg;
    private TiledLayer background;

	// pokemon image coordinates
	private int centerX;
	private int centerY;

	// the distance to move in the x axis
	private int dx = 1;
	private int dy = 1;

	// the center of the screen
	public final int CENTER_X = getWidth()/2;
	public final int CENTER_Y = getHeight()/2;


    // Playing field constants


    public static final int PLAYFIELD_WIDTH = 160;
    public static final int PLAYFIELD_HEIGHT = 256;

    // the shifted x,y origin of the game
    public final int PLAYFIELD_ORIGIN_X = (getWidth() - PLAYFIELD_WIDTH)/2;
    public final int PLAYFIELD_ORIGIN_Y = (getHeight() - PLAYFIELD_HEIGHT)/2;

    // the height of sections below and above pokemon
    public final int SEGMENT_SPACE = 96;

    // the base on which pokemon moves about
    public final int BASE = PLAYFIELD_ORIGIN_Y + PLAYFIELD_HEIGHT - SEGMENT_SPACE;

    // the max height the pokemon can jump
    public final int MAX_HEIGHT = 64;

    // a flag to indicate whether image is going up or not
    private boolean up = true;

    // initially set jumpHeight to MAX_HEIGHT
    private int jumpHeight = MAX_HEIGHT;

    // random number generator
    public Random random = new Random();

}