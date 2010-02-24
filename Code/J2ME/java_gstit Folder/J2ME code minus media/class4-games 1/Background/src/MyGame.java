import javax.microedition.midlet.MIDlet;
import javax.microedition.lcdui.Display;

public class MyGame extends MIDlet {

	MyGameCanvas gmCanvas;

	public MyGame() {
		gmCanvas = new MyGameCanvas();
	}

	public void startApp() {
		Display display = Display.getDisplay(this);
		gmCanvas.start();
		display.setCurrent(gmCanvas);
	}

	public void pauseApp() {
	}

	public void destroyApp(boolean unconditional) {
	}
}