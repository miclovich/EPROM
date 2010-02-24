import javax.microedition.midlet.MIDlet; 
import javax.microedition.lcdui.TextBox; 
import javax.microedition.lcdui.TextField; 
import javax.microedition.lcdui.Display; 

public class printerMidlet extends MIDlet {
    private TextBox textBox; 
    public printerMidlet() {
	textBox = new TextBox( "Your First Name?", "", 60,TextField.ANY); 
    }

    public void startApp() {
	Display.getDisplay(this).setCurrent(textBox);
    }

    public void pauseApp() {}
    public void destroyApp(boolean unconditional) {
    }
}

