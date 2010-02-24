import javax.microedition.midlet.*; 
import javax.microedition.lcdui.Display; 
import javax.microedition.lcdui.List; 
import javax.microedition.lcdui.Choice; 

public class printerMidlet extends MIDlet {
    List printList1; 
    List printList2;
    public printerMidlet() {
	printList1 = new List("Select a movie you like", Choice.MULTIPLE); 
	printList1.append("Matrix", null); 
		printList1.append("Crash", null); 
	printList1.append("Incredibles", null); 
        
       		String movies[] = {"Godfather", "Memento", "Vertigo"};
	        printList2 = new List( "Select a movie you like - List 2", Choice.IMPLICIT, movies, null); 
	}


	public void startApp() {
		 Display display = Display.getDisplay(this);
        	 display.setCurrent(printList1);
		 try {
			 Thread.currentThread().sleep(2000);
		 }
		 catch(Exception e) {}
		 display.setCurrent(printList2);
	}

	public void pauseApp() {}

	public void destroyApp(boolean unconditional) {}

}


