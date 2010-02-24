import javax.microedition.midlet.*; 
import javax.microedition.lcdui.Display; 
import javax.microedition.lcdui.Form;
import javax.microedition.lcdui.Gauge; 
import javax.microedition.lcdui.Spacer; 
import javax.microedition.lcdui.ImageItem;
import javax.microedition.lcdui.TextField;
import javax.microedition.lcdui.DateField;
import javax.microedition.lcdui.StringItem; 
import javax.microedition.lcdui.ChoiceGroup;
import javax.microedition.lcdui.Image;
import javax.microedition.lcdui.Choice; 

public class printerMidlet extends MIDlet {
	private Form form; 
	private Gauge gauge; 
	private Spacer spacer; 
	private ImageItem imageItem; 
	private TextField txtField; 

private DateField dateField; 
private StringItem stringItem; 
private ChoiceGroup choiceGroup; 
		
public printerMidlet() {
		form = new Form("Your Booking Details");
		 // a StringItem is not editable
		 stringItem = new StringItem("Your Id: ", "123456");
     	 form.append(stringItem); 
		 // you can accept Date, Time or DateTime formats 
		 dateField = new DateField("Your Date of Arrival: ",
        DateField.DATE);
      	 form.append(dateField);
		 // similar to using a TextBox
		 txtField = new TextField( "Your Name: ", "", 60, TextField.ANY); 
		form.append(txtField); 
		// similar to using a List 
		choiceGroup = new ChoiceGroup( "Room: ", Choice.EXCLUSIVE, new String[] {"Smoking", "Non-smoking"}, null); 
		form.append(choiceGroup); 
		
// put some space between the items to segregate 
		spacer = new Spacer(20, 20); form.append(spacer); 
		
// a gauge is used to show progress 
		gauge = new Gauge("Step 1 of 3", false, 3, 1); 
		form.append(gauge); 
		// an image may not be found
		try { 
			imageItem = new ImageItem( "Copyrighted by: ", Image.createImage("/copyright.png"),ImageItem.LAYOUT_DEFAULT, "copyright"); 
	            form.append(imageItem); 
	      } 
      	catch(Exception e) {
			System.out.println("Cannot find image");
		} 
}
public void startApp() {
		Display.getDisplay(this).setCurrent(form);
  }

	public void pauseApp() {}
	public void destroyApp(boolean unconditional) {
	}
}


