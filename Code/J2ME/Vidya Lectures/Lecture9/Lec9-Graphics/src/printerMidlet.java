import javax.microedition.lcdui.Canvas; 
import javax.microedition.midlet.*; 
import javax.microedition.lcdui.Display; 
import javax.microedition.lcdui.Graphics; 
import javax.microedition.lcdui.Image;

public class printerMidlet extends MIDlet { 
		Canvas canvas; 

		public printerMidlet() {
			 canvas = new canvas(); 
		} 
		public void startApp() {
	 	       Display display = Display.getDisplay(this); 
			display.setCurrent(canvas); 
			canvas.repaint(); 
		} 
		public void pauseApp() { } 
		public void destroyApp(boolean unconditional) { } 
} 
class canvas extends Canvas { 
    public void paint(Graphics g) { 
	int width = getWidth();
	int height = getHeight();
	Image image= null;
	try {
	    image = Image.createImage("/copyright.png");
	}
	catch(Exception e) {
	    e.printStackTrace();
	}
	g.setColor(0xffffff); 
	g.fillRect(0, 0, width, height); 
	g.drawImage(image, width/2,height/2 , Graphics.VCENTER | Graphics.HCENTER);

    }
} 
