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


	try{
	    Thread.currentThread().sleep(4000);
	} catch(Exception e) {}

	// inserts my lst name at the end of my first name. 
	// Notice how I have hardcoded the index. A better way would be to inset after a key is pressed so that the string from the textbox can be collected.
	textBox.insert("Setlur", 6);

	//Display.getDisplay(this).setCurrent(textBox);
	
    }

    public void pauseApp() {}
    public void destroyApp(boolean unconditional) {
    }
}

