import javax.microedition.midlet.*; 

public class PrinterApp extends MIDlet {
	public PrinterApp() {
		System.out.println("Constructor");
	}

	public void startApp() {
		System.out.println("Printing junk");
		destroyApp(true);
		notifyDestroyed();
	}

	public void pauseApp() {}
	public void destroyApp(boolean unconditional) {
		System.out.println("Destroying PrinterApp");
	}
}

